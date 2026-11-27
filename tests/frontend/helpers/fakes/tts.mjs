// Records what would have been said by the phone. Behaviour is controlled through globalThis.__tts.
const state = () => (globalThis.__tts ??= { spoken: [], stops: 0, languages: ['en-IN'], failSpeak: null });
export const TextToSpeech = {
  async isLanguageSupported({ lang }) {
    return { supported: state().languages.includes(lang) };
  },
  async speak(options) {
    if (state().failSpeak) throw new Error(state().failSpeak);
    state().spoken.push(options);
  },
  async stop() {
    state().stops++;
  },
};
