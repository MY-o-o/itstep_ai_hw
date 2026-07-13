import test from 'node:test';
import assert from 'node:assert/strict';
import slugify from './script.js';

test("slugify function", () => {
    assert.strictEqual(slugify(" Hello, World! "), "hello-world");
    assert.strictEqual(slugify(""), "");
});