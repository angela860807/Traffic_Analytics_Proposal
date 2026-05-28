#!/usr/bin/env node

const { spawn } = require("node:child_process");
const path = require("node:path");
const readline = require("node:readline");

const rootDir = path.resolve(__dirname, "..");
const pythonPath = path.join(rootDir, ".venv", "Scripts", "python.exe");
const streamScriptPath = path.join(rootDir, "scripts", "stream_video_file.py");
const childArgs = [streamScriptPath, ...process.argv.slice(2)];

const color = {
  dim: "\x1b[2m",
  reset: "\x1b[0m",
  bold: "\x1b[1m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  cyan: "\x1b[36m",
  gray: "\x1b[90m",
};

function c(value, tone) {
  return `${color[tone] || ""}${value}${color.reset}`;
}

function dot(tone) {
  return c("●", tone);
}

function parseKvLine(line) {
  const result = {};
  const pattern = /(\w+)=("[^"]*"|\S+)/g;
  let match;
  while ((match = pattern.exec(line)) !== null) {
    result[match[1]] = match[2].replace(/^"|"$/g, "");
  }
  return result;
}

function parseSpeed(value) {
  if (!value || value === "-") return null;
  const normalized = value.replace(/^VIOLATION:/, "");
  const [measured, limit] = normalized.split("/");
  const measuredNumber = Number.parseFloat(measured);
  const limitNumber = Number.parseFloat(limit);
  if (!Number.isFinite(measuredNumber)) return null;
  return {
    measured: measuredNumber,
    limit: Number.isFinite(limitNumber) ? limitNumber : null,
    violation: value.startsWith("VIOLATION:"),
  };
}

const eventSeparator = "=".repeat(77);
let currentEvent = {
  finalized: false,
  ocr: false,
};

function resetEvent() {
  currentEvent = {
    finalized: false,
    ocr: false,
  };
}

function printEventSeparatorIfComplete() {
  if (!currentEvent.finalized || !currentEvent.ocr) {
    return;
  }
  console.log(c(eventSeparator, "gray"));
  resetEvent();
}

function closeIncompleteEventBeforeNextVehicle() {
  if (!currentEvent.finalized && !currentEvent.ocr) {
    return;
  }
  console.log(c(eventSeparator, "gray"));
  resetEvent();
}

function printConfig(line) {
  try {
    const config = JSON.parse(line);
    console.log(c("\n시연 스트리밍 시작", "bold"));
    console.log(
      [
        `${c("영상", "gray")} ${config.video}`,
        `${c("카메라", "gray")} ${config.cameraCode}`,
        `${c("FPS", "gray")} ${config.targetFps}`,
        `${c("업로드", "gray")} x${config.uploadScale}`,
        `${c("GUI", "gray")} x${config.displayScale}`,
        `${c("딜레이", "gray")} ${config.previewDelaySeconds}s`,
      ].join("  ")
    );
    console.log(c("─".repeat(82), "gray"));
  } catch {
    console.log(line);
  }
}

function printFrame(line) {
  const kv = parseKvLine(line);
  const speed = parseSpeed(kv.speed);
  const status = kv.streamStatus || "-";

  if (status === "TRACKING" && speed?.violation) {
    if (currentEvent.finalized) {
      closeIncompleteEventBeforeNextVehicle();
    }
    const speedText =
      speed.limit === null
        ? `${speed.measured.toFixed(1)}km/h`
        : `${speed.measured.toFixed(1)} / ${speed.limit.toFixed(0)}km/h`;
    console.log(`${dot("red")} ${c("과속 차량 감지", "red")}  ${c(speedText, "red")}`);
    return;
  }

  if (status === "TRACKING") {
    if (currentEvent.finalized) {
      closeIncompleteEventBeforeNextVehicle();
    }
    console.log(`${dot("green")} ${c("차량 추적 중", "cyan")}`);
    return;
  }

  if (status === "FINALIZED") {
    const speedText = speed
      ? `${speed.measured.toFixed(1)}km/h${speed.violation ? " 과속" : ""}`
      : "-";
    console.log(`${dot("yellow")} ${c("차량 분석 완료", "yellow")}  계산 속도=${speedText}`);
    currentEvent.finalized = true;
    printEventSeparatorIfComplete();
    return;
  }

  if (status === "IDLE") {
    return;
  }

  console.log(line);
}

function printOcr(line) {
  const kv = parseKvLine(line);
  const plate = kv.plateNumber || "-";
  const status = kv.analysisStatus || "-";
  const tone = status === "FLOW_EVENT_CREATED" ? "green" : status === "OCR_FAILED" ? "red" : "yellow";
  const statusLabel = {
    FLOW_EVENT_CREATED: "저장 완료",
    DUPLICATE_SKIPPED: "중복 감지",
    OCR_FAILED: "번호판 인식 실패",
  }[status] || "처리 완료";
  console.log(`${dot(tone)} ${c("번호판 인식 결과", tone)}  ${c(plate, tone)}  ${statusLabel}`);
  currentEvent.ocr = true;
  printEventSeparatorIfComplete();
}

function printSummary(line) {
  const kv = parseKvLine(line);
  closeIncompleteEventBeforeNextVehicle();
  console.log(c("─".repeat(82), "gray"));
  console.log(
    `${dot("green")} ${c("시연 종료", "bold")}  분석 차량=${kv.finalizedEvents || "-"}대`
  );
}

function printLine(line) {
  const trimmed = line.trim();
  if (!trimmed) return;

  if (trimmed.startsWith("{") && trimmed.endsWith("}")) {
    printConfig(trimmed);
  } else if (trimmed.startsWith("frame=")) {
    printFrame(trimmed);
  } else if (trimmed.startsWith("ocrStatus ")) {
    printOcr(trimmed);
  } else if (trimmed.startsWith("highresFrame=")) {
    return;
  } else if (trimmed.startsWith("uploadedFrames=")) {
    printSummary(trimmed);
  } else if (trimmed.startsWith("stopReason=")) {
    console.log(`${dot("gray")} ${c("사용자 요청으로 시연을 중지했습니다.", "gray")}`);
  } else {
    console.log(trimmed);
  }
}

const child = spawn(pythonPath, childArgs, {
  cwd: rootDir,
  stdio: ["inherit", "pipe", "pipe"],
});

readline.createInterface({ input: child.stdout }).on("line", printLine);
readline.createInterface({ input: child.stderr }).on("line", (line) => {
  console.error(c(line, "red"));
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 0);
});
