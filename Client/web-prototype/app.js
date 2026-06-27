const API_BASE = "http://127.0.0.1:8787";

const labels = {
  realm_01: "炼气一层",
  map_01: "新手矿洞",
  quest_first_dig: "第一次挖宝",
  quest_first_antique: "获得未知古物",
  quest_first_appraisal: "第一次鉴宝",
  quest_first_equip: "穿戴装备",
  quest_first_battle: "第一次打怪",
  quest_first_elite: "挑战精英",
  quest_first_realm: "第一次境界突破",
  quest_first_boss: "击败首领",
  quest_first_offline_reward: "第一次离线收益",
  quest_first_daily: "开启日常",
  antique_bronze_mirror: "青铜古镜",
};

const state = {
  config: {},
  player: null,
  selectedAntiqueUid: null,
  busy: false,
};

const $ = (id) => document.getElementById(id);

async function api(method, path, payload) {
  const options = { method, headers: {} };
  if (payload) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(payload);
  }
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "UNKNOWN" }));
    throw new Error(error.error || `HTTP_${response.status}`);
  }
  return response.json();
}

async function loadLocalConfig() {
  const files = ["quests", "maps", "battle_stages", "antiques"];
  const entries = await Promise.all(
    files.map(async (name) => {
      const response = await fetch(`/Config/json/${name}.json`);
      return [name, await response.json()];
    })
  );
  state.config = Object.fromEntries(entries);
}

function setBusy(isBusy) {
  state.busy = isBusy;
  [
    "loginButton",
    "claimQuestButton",
    "claimIdleButton",
    "appraiseButton",
    "battleButton",
  ].forEach((id) => {
    const button = $(id);
    if (button) button.disabled = isBusy;
  });
}

function setStatus(text, ok = true) {
  $("connectionStatus").textContent = text;
  $("connectionStatus").style.background = ok ? "var(--blue)" : "var(--red)";
}

function findById(listName, id) {
  return (state.config[listName] || []).find((row) => row.id === id);
}

function rewardText(reward) {
  if (!reward || reward === "none") return "无";
  return reward
    .split("|")
    .map((chunk) => {
      const [itemId, amount] = chunk.split(":");
      const itemName = itemId === "spirit_stone" ? "灵石" : itemId;
      return `${itemName} x${amount}`;
    })
    .join("，");
}

function render() {
  const player = state.player;
  if (!player) return;

  $("loginPanel").classList.add("hidden");
  $("gamePanel").classList.remove("hidden");

  $("nickname").textContent = player.profile.nickname;
  $("realm").textContent = `境界 ${labels[player.profile.realm_id] || player.profile.realm_id}`;
  $("power").textContent = player.profile.power;
  $("spiritStone").textContent = player.assets.spirit_stone || 0;
  $("jade").textContent = player.assets.jade || 0;
  $("token").textContent = player.assets.appraisal_token || 0;

  const map = findById("maps", player.profile.current_map_id);
  $("mapName").textContent = labels[player.profile.current_map_id] || player.profile.current_map_id;
  $("idleText").textContent = map
    ? `挂机中，每分钟基础产出 ${map.base_reward_per_min} 灵石。`
    : "挂机中，每分钟产出灵石。";

  const quest = findById("quests", player.main_quest_id);
  $("questTitle").textContent = quest ? labels[quest.name_key] || quest.name_key : "主线已完成";
  $("questTarget").textContent = quest ? `目标 ${quest.target}，奖励 ${rewardText(quest.reward)}` : "进入自由循环";

  renderAntiques();
  renderBattleStage();
}

function renderAntiques() {
  const list = $("antiqueList");
  list.innerHTML = "";
  const antiques = state.player.antiques || [];
  $("appraisalDot").classList.toggle("off", !antiques.some((item) => item.state === "unidentified"));

  if (antiques.length === 0) {
    list.innerHTML = `<div class="result-box">暂无古物，先去挖宝。</div>`;
    return;
  }

  antiques.forEach((item) => {
    const template = findById("antiques", item.template_id);
    const row = document.createElement("button");
    row.className = `item-row ${state.selectedAntiqueUid === item.uid ? "selected" : ""}`;
    row.type = "button";
    row.innerHTML = `
      <span>${template ? labels[template.name_key] || template.name_key : item.template_id}</span>
      <strong>${item.state === "appraised" ? `${item.final_price} 灵石` : "未鉴定"}</strong>
    `;
    row.addEventListener("click", () => {
      state.selectedAntiqueUid = item.uid;
      renderAntiques();
    });
    list.appendChild(row);
  });
}

function renderBattleStage() {
  const stage = findById("battle_stages", "stage_001");
  if (!stage) return;
  $("stagePower").textContent = stage.recommend_power;
  $("stageReward").textContent = rewardText(stage.first_reward);
}

async function login() {
  try {
    setBusy(true);
    setStatus("读取配置");
    await loadLocalConfig();
    await api("GET", "/config/latest");
    setStatus("游客登录");
    const deviceId = localStorage.getItem("device_id") || crypto.randomUUID();
    localStorage.setItem("device_id", deviceId);
    await api("POST", "/auth/guest-login", {
      device_id: deviceId,
    });
    setStatus("同步存档");
    state.player = await api("GET", "/game/sync");
    setStatus("已连接");
    render();
  } catch (error) {
    setStatus(`失败 ${error.message}`, false);
  } finally {
    setBusy(false);
  }
}

async function refreshPlayer() {
  state.player = await api("GET", "/game/sync");
  render();
}

async function claimIdle() {
  try {
    setBusy(true);
    const result = await api("POST", "/idle/claim", {});
    $("idleText").textContent = `领取成功：${rewardText(result.rewards.map((item) => `${item.item_id}:${item.amount}`).join("|"))}`;
    await refreshPlayer();
  } catch (error) {
    $("idleText").textContent = `领取失败：${error.message}`;
  } finally {
    setBusy(false);
  }
}

async function claimQuest() {
  try {
    setBusy(true);
    const questId = state.player.main_quest_id;
    const result = await api("POST", "/quest/claim", { quest_id: questId });
    $("questTarget").textContent = `已领取：${result.rewards.map((item) => `${item.item_id} x${item.amount}`).join("，")}`;
    await refreshPlayer();
  } catch (error) {
    $("questTarget").textContent = `领取失败：${error.message}`;
  } finally {
    setBusy(false);
  }
}

async function appraise() {
  try {
    setBusy(true);
    $("appraisalResult").textContent = "鉴定中...";
    await new Promise((resolve) => setTimeout(resolve, 650));
    const result = await api("POST", "/antique/appraise", {});
    $("appraisalResult").textContent = `估价完成：${result.antique.final_price} 灵石，结果 ${result.result_type}`;
    await refreshPlayer();
  } catch (error) {
    $("appraisalResult").textContent = `鉴定失败：${error.message}`;
  } finally {
    setBusy(false);
  }
}

async function battle() {
  try {
    setBusy(true);
    $("battleResult").textContent = "开战...";
    await api("POST", "/battle/start", { stage_id: "stage_001" });
    await animateBattle();
    const result = await api("POST", "/battle/finish", { stage_id: "stage_001" });
    $("battleResult").textContent = `胜利：${rewardText(result.rewards.map((item) => `${item.item_id}:${item.amount}`).join("|"))}`;
    await refreshPlayer();
  } catch (error) {
    $("battleResult").textContent = `战斗失败：${error.message}`;
  } finally {
    setBusy(false);
  }
}

async function animateBattle() {
  const hero = $("heroHp");
  const monster = $("monsterHp");
  hero.style.width = "100%";
  monster.style.width = "100%";
  const frames = [
    ["86%", "78%"],
    ["72%", "54%"],
    ["58%", "24%"],
    ["48%", "0%"],
  ];
  for (const [heroWidth, monsterWidth] of frames) {
    await new Promise((resolve) => setTimeout(resolve, 420));
    hero.style.width = heroWidth;
    monster.style.width = monsterWidth;
  }
}

$("loginButton").addEventListener("click", login);
$("claimIdleButton").addEventListener("click", claimIdle);
$("claimQuestButton").addEventListener("click", claimQuest);
$("appraiseButton").addEventListener("click", appraise);
$("battleButton").addEventListener("click", battle);

setStatus("等待启动");
