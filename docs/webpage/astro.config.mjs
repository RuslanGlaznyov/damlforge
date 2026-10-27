// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightLinksValidator from 'starlight-links-validator';

export default defineConfig({
	integrations: [
		starlight({
			title: 'DamlForge',
			description: 'Write Daml smart contracts for Canton in Python syntax.',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/noders-team/damlforge' }],
			sidebar: [{ label: 'User guide', items: [{ autogenerate: { directory: 'guide' } }] }],
			plugins: [starlightLinksValidator()],
		}),
	],
});
