# UI Design Guidelines

## Design Philosophy
- **Modern & Clean**: Use ample whitespace, rounded corners, and subtle shadows.
- **Interactive**: Elements should respond to user interaction (hover effects, transitions).
- **Consistent**: Use defined CSS variables for colors, spacing, and typography.
- **Simplicity (For Beginners)**: 
  - Hide complex options by default.
  - Use smart defaults (e.g., auto-detection instead of manual selection).
  - Use plain language labels (e.g., "Paste Link" instead of "Input Content").

## Core Components

### Page Layout
- **Container**: Use `.page-container` (or similar) with `padding: 24px` and `background-color: var(--bg-secondary)`.
- **Animation**: Apply `.fade-up` class to the root element for smooth entry.

### Cards & Panels
- **Style**: White background, `border-radius: 16px`, `box-shadow: var(--shadow-sm)`.
- **Hover**: Add `.hover-card` class for lift effect and increased shadow on hover.
- **Header**: Separate header section with title and actions.

### Tables
- **Style**: Clean look, no outer borders.
- **Header**: Light gray background (`#f9fafb`), uppercase labels, bold text.
- **Rows**: Taller rows (`height: 64px+`) for better readability.
- **Implementation**:

  ```scss
  .custom-table {
    --el-table-border-color: #f3f4f6;
    :deep(th) { background: #f9fafb; height: 56px; }
    :deep(td) { height: 72px; }
    :deep(.el-table__inner-wrapper::before) { display: none; } // Remove bottom border
  }
  ```

### Buttons
- **Primary**: Gradient or solid primary color.
- **Action Buttons**: Use `.action-btn` for consistent hover transition.
- **Shadow**: Use `.shadow-btn` for primary actions.

## CSS Utilities (in `src/styles/index.scss`)
- `.fade-up`: Entry animation.
- `.hover-card`: Hover lift effect.
- `.slide-in`: Staggered entry animation.

## Color Palette
- **Primary**: `var(--primary-color)` (Blue/Purple gradient)
- **Background**: `var(--bg-secondary)` (Light gray #f9fafb)
- **Text**: `var(--text-primary)` (Dark gray #1f2937)
