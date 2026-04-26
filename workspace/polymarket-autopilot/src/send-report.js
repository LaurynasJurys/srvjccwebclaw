import { execSync } from "node:child_process";

const output = execSync("node src/report.js", { encoding: "utf8" });
console.log(output);
console.log("\nNext step: wire this text through OpenClaw message delivery or a cron-owned agentTurn.");
