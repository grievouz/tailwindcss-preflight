<div align="center">
	<img height="140px" src="docs/logo.svg" alt="preflight">
	<br>
	“An opinionated set of base styles”
	<br>
	<i>- <a href="https://tailwindcss.com/docs/preflight">Tailwind.com</a></i>
</div>

## Usage

```html
<link href="https://cdn.jsdelivr.net/npm/tailwindcss-preflight@1.1.1/preflight.min.css" rel="stylesheet" />
```

## Installation

```properties
npm install tailwindcss-preflight --save
```

Using <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import">ES6 imports</a>:

```typescript
import "tailwindcss-preflight";
```

## Customization

The CSS works directly in browsers without Tailwind or a build step. By default,
it uses the upstream font stacks and normal font feature/variation settings.
You can optionally override them with native CSS custom properties:

```css
:root {
  --default-font-family: Arial, sans-serif;
  --default-font-feature-settings: "liga" 1;
  --default-font-variation-settings: "wght" 400;
  --default-mono-font-family: "Courier New", monospace;
  --default-mono-font-feature-settings: normal;
  --default-mono-font-variation-settings: normal;
}
```

These overrides are optional; omitted variables use built-in fallbacks. Use valid
CSS values for their corresponding properties. Font features/variations require
support from the chosen font.

**Release note:** this describes the source on this branch; the pinned `1.1.1`
CDN URL above does not include these changes until a new version is published.

## Development

Run `python3 -m unittest discover -s tests -v` with Chromium/Chrome installed
(or set `CHROME_BIN`). See [upstream provenance and update instructions](docs/upstream.md).

## Why did you create this package?

For anyone who wants to use <a href="https://tailwindcss.com/docs/preflight">Preflight</a> but doesn't feel like pulling in all of <a href="https://tailwindcss.com/">Tailwind CSS</a>.

## Credits

<a href="https://tailwindcss.com/docs/preflight">Preflight</a> is built on top of <a href="https://github.com/sindresorhus/modern-normalize">modern-normalize</a> which itself is based on <a href="https://github.com/necolas/normalize.css">normalize.css</a>.
<br>
All credit goes to the respective code authors:

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/necolas"
        ><img
          src="https://avatars.githubusercontent.com/u/239676?v=3?s=100"
          width="100px;"
          alt=""
        />
				<br />
				<sub><b>Nicolas Gallagher</b></sub></a
      >
    </td>
		<td align="center">
      <a href="https://github.com/jonathantneal"
        ><img
          src="https://avatars.githubusercontent.com/u/188426?v=3?s=100"
          width="100px;"
          alt=""
        />
				<br />
				<sub><b>Jonathan Neal</b></sub></a>
    </td>
		<td align="center">
      <a href="https://github.com/sindresorhus"
        ><img
          src="https://avatars.githubusercontent.com/u/170270?v=3?s=100"
          width="100px;"
          alt=""
        />
				<br />
				<sub><b>Sindre Sorhus</b></sub></a>
    </td>
		<td align="center">
      <a href="https://github.com/adamwathan"
        ><img
          src="https://avatars.githubusercontent.com/u/4323180?v=3?s=100"
          width="100px;"
          alt=""
        />
				<br />
				<sub><b>Adam Wathan</b></sub></a>
    </td>
		<td align="center">
      <a href="https://github.com/jonathantneal"
        ><img
          src="https://avatars.githubusercontent.com/u/882133?v=3?s=100"
          width="100px;"
          alt=""
        />
				<br />
				<sub><b>Jonathan Reinink</b></sub></a>
    </td>
  </tr>
</table>
