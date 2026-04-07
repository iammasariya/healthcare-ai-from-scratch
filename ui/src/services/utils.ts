export const SAMPLE_NOTE =
  "Patient presents with fatigue and intermittent dizziness for 3 days. BP 142/88, HR 84, Temp 98.4F. Denies chest pain or dyspnea. Past history of type 2 diabetes and hypertension. Current meds include metformin 1000mg BID and lisinopril 10mg daily.";

export function fuzzyTokenSimilarity(a: string, b: string): number {
  const tokenize = (text: string) =>
    text
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, " ")
      .split(/\s+/)
      .filter(Boolean);

  const setA = new Set(tokenize(a));
  const setB = new Set(tokenize(b));

  if (setA.size === 0 && setB.size === 0) {
    return 1;
  }

  const intersection = [...setA].filter((token) => setB.has(token)).length;
  const union = new Set([...setA, ...setB]).size;
  return union === 0 ? 0 : intersection / union;
}
