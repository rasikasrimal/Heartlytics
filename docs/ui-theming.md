# UI Theming

HeartLytics supports light and dark color themes. The default is **light** and
users can toggle using the navbar button or the setting on the Settings page.
The selection is stored in `localStorage` and a long-lived `theme` cookie so the
server can render pages in the correct theme without a flash of incorrect
colors.

## Usage

No additional code is required to theme new Plotly or Chart.js charts. The
`static/theme.charts.js` module patches the libraries globally so all charts pick
up the current theme. In dark mode, chart backgrounds are transparent so they
blend with the page.

If a new visualization library is introduced, listen for the `themechange` event
on `window` and apply colors from CSS variables such as `--bs-body-bg` and
`--bs-body-color`.

Auth pages, including the redesigned sign-up and forgot-password flows, consume reusable Bootstrap components so card backgrounds, buttons, and countdown badges adapt automatically to the selected theme.
