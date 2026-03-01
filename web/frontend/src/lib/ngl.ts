/** Suppress noisy NGL console output (deprecation warnings + stage log messages). */
let _patched = false;
export function suppressNglDeprecationWarnings(): void {
  if (_patched) return;
  _patched = true;

  const origWarn = console.warn;
  console.warn = (...args: unknown[]) => {
    if (typeof args[0] === "string" && args[0].includes("useLegacyLights")) return;
    origWarn.apply(console, args);
  };

  const origLog = console.log;
  console.log = (...args: unknown[]) => {
    if (typeof args[0] === "string" && args[0].startsWith("STAGE LOG")) return;
    origLog.apply(console, args);
  };
}
