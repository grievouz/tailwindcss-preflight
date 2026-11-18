<div align="center">
	<img height="140px" src="docs/logo.svg" alt="preflight">
	<br>
	“An opinionated set of base styles”
	<br>
	<i>- <a href="https://tailwindcss.com/docs/preflight">Tailwind.com</a></i>
</div>

## Usage

```html
<link href="https://cdn.jsdelivr.net/npm/tailwindcss-preflight@latest/preflight.css" rel="stylesheet" />
```

## Installation

```properties
npm install tailwindcss-preflight --save
```

Using a CSS-aware bundler (not plain Node.js runtime CSS loading):

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

For CSS imports, use `@import "tailwindcss-preflight/preflight.css";`.
The CDN URL follows npm’s `latest` release automatically (subject to CDN caching),
including future major versions, so it does not need a version edit for each release.
For reproducible production builds, replace `latest` with an exact published version.
A GitHub release alone does not update npm or CDNs.

## Development

Run `python3 -m unittest discover -s tests -v` with Chromium/Chrome installed
(or set `CHROME_BIN`). Python 3.9+, Node.js 24 and npm are also required for offline
package installation/entry-point checks. No dependency installation or CSS build
is needed. See [upstream provenance](docs/upstream.md), [changelog](CHANGELOG.md)
and [release procedure / trusted publishing setup](docs/releases.md).

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
