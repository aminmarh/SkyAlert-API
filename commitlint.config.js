module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'subject-max-length': [2, 'always', 95], // Limiter les messages à 95 caractères
  },
};
