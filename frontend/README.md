# Frontend Development Status

## Tech Stack & Dependencies

### Core Technologies
- Vue.js 3 (primarily using Options API, with some Composition API in UI components)
- Vite as the build tool
- Pinia for state management
- Vue Router for navigation
- TailwindCSS for styling
- PrimeVue UI component library

### Key Dependencies
- CodeMirror for code editing
- Monaco Editor for advanced code editing features
- Chart.js for data visualization
- Markdown-it for markdown rendering

## Open Source & AI Assistance

### Open Source Components
This project heavily utilizes open-source components and libraries:
- PrimeVue components for UI elements
- CodeMirror for the code editor
- Various Vue.js community plugins
- TailwindCSS for utility-first styling

### AI-Assisted Development
Some visual styling and UI improvements were developed with the assistance of Large Language Models (LLMs):
- Minor CSS and Tailwind adjustments
- Small UI component refinements
- Visual tweaks and polish

## Current State

This frontend codebase contains a significant amount of boilerplate code and unused components. This is intentional and serves several purposes in my development process:

### Boilerplate Code
- I started this project with a template that included many pre-built components and utilities
- This boilerplate gives me a solid foundation for rapid development and prototyping
- Many components in the `uikit` directory are kept as my personal reference library

### Unused Components
- Several components in the `views/uikit` directory aren't currently used in production
- These components serve as my personal component library and documentation
- I use them as reference when implementing new features or as templates for new components

### Redundant/Duplicate Components
- Some components may appear redundant (e.g., `AppConfigurator.vue` and `FloatingConfigurator.vue`)
- I keep these to maintain flexibility in UI customization
- I may consolidate them in future iterations based on how I use them

## My Development Strategy

### Why Keep Unused Code?
1. **Development Speed**: Having pre-built components lets me prototype quickly
2. **Personal Reference**: Unused components serve as my personal documentation and examples
3. **Future-Proofing**: I can quickly adapt components for new features
4. **Learning Tool**: The boilerplate code helps me learn and experiment with different approaches

### My Cleanup Strategy
- I'll remove components only when:
  - I'm certain they're completely unused
  - I've replaced them with better implementations
  - They're causing maintenance issues
- I'll periodically review the codebase to identify truly obsolete code

## Important Directories

- `src/views/uikit/` - My personal component library and documentation
- `src/service/` - Service implementations (some with mock data for testing)
- `src/layout/` - Layout components I use across the application
- `src/codeLayout/` - Specialized layout for code-related views
