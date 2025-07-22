// jest.config.js
const nextJest = require('next/jest')

/** Provide the path to your Next.js app to load its config */
const createJestConfig = nextJest({
  dir: './',
})

/** Add any custom config you need here */
const customJestConfig = {
  testEnvironment: 'jest-environment-jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    // Handle CSS imports
    '\\.(css|scss)$': 'identity-obj-proxy',
    // Handle your `@/` alias to src/
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testPathIgnorePatterns: ['/node_modules/', '/.next/'],
}

module.exports = createJestConfig(customJestConfig)
