// Loaded only by the local, dependency-free test harness. No network requests.
(() => {
  const result = document.getElementById('result');
  let checks = 0;
  function assert(condition, description) {
    if (!condition) throw new Error(description);
    checks++;
  }
  function equal(actual, expected, description) {
    assert(actual === expected, `${description}: ${actual} !== ${expected}`);
  }
  const root = document.documentElement;
  const mono = document.getElementById('mono');
  const button = document.getElementById('button');
  const properties = ['fontFamily', 'fontFeatureSettings', 'fontVariationSettings'];
  const variables = ['font-family', 'font-feature-settings', 'font-variation-settings'];

  try {
    const rule = [...document.styleSheets[0].cssRules].find(rule => rule.selectorText === 'html, :host');
    assert(Boolean(rule), 'root rule exists');
    for (const property of variables) {
      assert(rule.style.getPropertyValue(property).startsWith('var('), `${property} parses as native CSS`);
    }
    const reference = document.createElement('span');
    reference.style.fontFamily = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', 'Noto Sans', Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji'";
    document.body.append(reference);
    equal(getComputedStyle(root).fontFamily, getComputedStyle(reference).fontFamily, 'sans fallback');
    reference.style.fontFamily = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace";
    equal(getComputedStyle(mono).fontFamily, getComputedStyle(reference).fontFamily, 'mono fallback');
    for (const element of [root, mono]) {
      equal(getComputedStyle(element).fontFeatureSettings, 'normal', 'feature fallback');
      equal(getComputedStyle(element).fontVariationSettings, 'normal', 'variation fallback');
    }

    const sansValues = ['Arial, serif', '"liga" 0', '"wght" 512'];
    const monoValues = ['"Courier New", monospace', '"calt" 0', '"wght" 650'];
    function configure(element, sans, code) {
      variables.forEach((property, index) => {
        element.style.setProperty(`--default-${property}`, sans[index]);
        element.style.setProperty(`--default-mono-${property}`, code[index]);
      });
    }
    function checkValues(element, values, description) {
      properties.forEach((property, index) => {
        reference.style[property] = values[index];
        equal(getComputedStyle(element)[property], reference.style[property], `${description} ${property}`);
      });
    }
    configure(root, sansValues, monoValues);
    checkValues(root, sansValues, 'root overrides');
    checkValues(mono, monoValues, 'mono overrides');
    checkValues(button, sansValues, 'form control inheritance');

    const host = document.createElement('div');
    document.body.append(host);
    const shadow = host.attachShadow({mode: 'open'});
    const style = document.createElement('style');
    style.textContent = [...document.styleSheets[0].cssRules].map(rule => rule.cssText).join('\n');
    shadow.append(style);
    const shadowCode = document.createElement('code');
    shadowCode.textContent = 'shadow code';
    shadow.append(shadowCode);
    const shadowSans = ['Verdana, sans-serif', '"kern" 0', '"wdth" 90'];
    const shadowMono = ['monospace', '"liga" 0', '"wght" 450'];
    configure(host, shadowSans, shadowMono);
    checkValues(host, shadowSans, 'shadow host overrides');
    checkValues(shadowCode, shadowMono, 'shadow mono overrides');
    result.textContent = `PASS: ${checks} browser assertions (defaults, all six overrides, inheritance, shadow DOM)`;
  } catch (error) {
    result.textContent = `FAIL: ${error.stack}`;
  }
})();
