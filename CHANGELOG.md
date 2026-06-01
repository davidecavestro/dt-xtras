# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.9] - 2026-06-01
### :boom: BREAKING CHANGES
- due to [`5002871`](https://github.com/davidecavestro/dt-xtras/commit/5002871c2591171c87218b38402fb0154e55bb06) - bump up devcontainer pg to 18 *(commit by [@davidecavestro](https://github.com/davidecavestro))*:

  bump up devcontainer pg to 18

- due to [`0c19f5e`](https://github.com/davidecavestro/dt-xtras/commit/0c19f5e439d12e4c7027bdb4d0b2d88b3487fe4a) - remove DT_API_KEY to strengthen security *(commit by [@davidecavestro](https://github.com/davidecavestro))*:

  remove DT_API_KEY to strengthen security

- due to [`cee3228`](https://github.com/davidecavestro/dt-xtras/commit/cee322883dc0f9206b65e44d067213b7992e9646) - loose coupling *(commit by [@davidecavestro](https://github.com/davidecavestro))*:

  loose coupling


### :sparkles: New Features
- [`5882c82`](https://github.com/davidecavestro/dt-xtras/commit/5882c82156bdb0af642b4b41541a9a407072b798) - add expand/zoom/fit handles to graphs *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`c1931ec`](https://github.com/davidecavestro/dt-xtras/commit/c1931ec75e4e30968beb65ff77f815480ab18e4d) - better Navigation Tree readability *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`5224979`](https://github.com/davidecavestro/dt-xtras/commit/52249797dca5417a1a9f835d725d295d7fae165a) - use datagrid for dashboard *(commit by [@davidecavestro](https://github.com/davidecavestro))*

### :bug: Bug Fixes
- [`55178c9`](https://github.com/davidecavestro/dt-xtras/commit/55178c9b788cc719e269ea8ea5b9f237f5e1f444) - the navigation tree is broken, as it shares treenodes data having different paths *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`c4411c6`](https://github.com/davidecavestro/dt-xtras/commit/c4411c6815a8aa96883dd77a4b6ec2f252cb1867) - broken tests for backend *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`8a24da6`](https://github.com/davidecavestro/dt-xtras/commit/8a24da6a739562932f112d1dac3593f295803537) - hierarchical tree is broken *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`a9097b5`](https://github.com/davidecavestro/dt-xtras/commit/a9097b5616001b87490f39c751d967ac2735978c) - wrong colors on tags tree *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`c7321ac`](https://github.com/davidecavestro/dt-xtras/commit/c7321ac3f292e9194ef65f806dda40c8c6406f5f) - broken test_login_success *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`dec38fb`](https://github.com/davidecavestro/dt-xtras/commit/dec38fbce00b49e176f512d119f2c2f2caac3b49) - conftest.py returns a plain text token that's not a valid JWT format *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`49a2d8e`](https://github.com/davidecavestro/dt-xtras/commit/49a2d8e541f1751108bb10d26ef009322e92e2cd) - broken hierarchy building logic *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`d0aca8c`](https://github.com/davidecavestro/dt-xtras/commit/d0aca8c4479ba28db005bb305b762afa250b000a) - tree endpoint prjs count and metrics *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`83308ed`](https://github.com/davidecavestro/dt-xtras/commit/83308ed1935311572e1861ba123d051a18731a0d) - mount volumes for DT on dev *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`737b298`](https://github.com/davidecavestro/dt-xtras/commit/737b29814df151bdfa1b5eb2b43d4b94c90105e0) - restore code eaten by AI *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`7f7912d`](https://github.com/davidecavestro/dt-xtras/commit/7f7912dc44ceaa7220874f9adc3e926bada00ba4) - broken tree metrics aggregation *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`d954ec3`](https://github.com/davidecavestro/dt-xtras/commit/d954ec35a403ebdfe0b1f7f70cbb218d9240076b) - treetable metrics broken *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`a9961a4`](https://github.com/davidecavestro/dt-xtras/commit/a9961a4b3c1c79be6ecbf3378fdc01e79993d097) - duplicated orphan tags on hierarchy *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`a93f163`](https://github.com/davidecavestro/dt-xtras/commit/a93f163f7b6fcd03a5f857d404841b7ef3fc3335) - broken metrics and related projects on dashboard *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`d7571f6`](https://github.com/davidecavestro/dt-xtras/commit/d7571f6ee940f53eadef49d74c878db55d6f3ac8) - readme example *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`b926345`](https://github.com/davidecavestro/dt-xtras/commit/b926345c92c843c2d9b25eaa05c7893274a76ccb) - tailwindcss upgrade broke FE *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`33ef4e5`](https://github.com/davidecavestro/dt-xtras/commit/33ef4e518d53f0e70291ef9fd615f3fab1b62ea6) - missing color on dashboard tag badges *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`565ae18`](https://github.com/davidecavestro/dt-xtras/commit/565ae18097c8e3f162729e00bf26f224ae66f75a) - frontend coverage is wrong *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`ec2ef1b`](https://github.com/davidecavestro/dt-xtras/commit/ec2ef1bb884b3c576ff31044bd8acbbfb08e3f10) - remove coverage output frommmmmmmm  version control *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`999a463`](https://github.com/davidecavestro/dt-xtras/commit/999a46319dbf7803bbbd41aac86766d60ac5e8ea) - broken main on backend dev *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`705b9fa`](https://github.com/davidecavestro/dt-xtras/commit/705b9fa61815c95547b9dd358ff67372e2449fac) - broken Tags Graph raw mode *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`cd60eb3`](https://github.com/davidecavestro/dt-xtras/commit/cd60eb389152e49fcaf477396a219bc55816482c) - TAxonomy tags list doesn't show taxonomy name *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`95c596e`](https://github.com/davidecavestro/dt-xtras/commit/95c596e435dc19b2d2cc919402b89b43fffee823) - taxonomy create/edit not using modal *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`8ac21a1`](https://github.com/davidecavestro/dt-xtras/commit/8ac21a1fcfa1a086dfd3be8ef328bc70e7983e95) - broken project bulk actions *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`7198bf2`](https://github.com/davidecavestro/dt-xtras/commit/7198bf292cd2fa9f35fe80f5675f4894a35a33b2) - broken tests *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`fbd0ca9`](https://github.com/davidecavestro/dt-xtras/commit/fbd0ca9fd208ba797c0446d4533436e3deb923df) - refactor broke backend services *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`6f2f122`](https://github.com/davidecavestro/dt-xtras/commit/6f2f1220a231463b40597001598ddab8160223a8) - tag graph broken in hierarchiical mode *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`eb5c75b`](https://github.com/davidecavestro/dt-xtras/commit/eb5c75b8a9102f462f02f40f018c15895716cb7d) - provide clear visual feedback for desktop users on what's clickable *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`0c19f5e`](https://github.com/davidecavestro/dt-xtras/commit/0c19f5e439d12e4c7027bdb4d0b2d88b3487fe4a) - remove DT_API_KEY to strengthen security *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`0f3e5a3`](https://github.com/davidecavestro/dt-xtras/commit/0f3e5a3d113210c961bfcb6984a635a7e9f1ced8) - taxonomy priority not working *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`aefa20b`](https://github.com/davidecavestro/dt-xtras/commit/aefa20bcd4f21afe55805c873ab55bc603ec0416) - broken requirements *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`d8423f6`](https://github.com/davidecavestro/dt-xtras/commit/d8423f61adbeceeaf694eedb916c3012bb3a0e3a) - uniform buttons appearance across views *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`3bdebba`](https://github.com/davidecavestro/dt-xtras/commit/3bdebbafea447f0cbff4dfa0e5da500414b7f9f9) - sbom populator for local testing isbroken *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`841a16e`](https://github.com/davidecavestro/dt-xtras/commit/841a16e4b2af52f0c5cce923476e998a1b7bb8c0) - broken pagination for projects and tags *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`adee042`](https://github.com/davidecavestro/dt-xtras/commit/adee042a805cd4eebaa0b7b471cfa3e348ed37b3) - filtering is broken *(commit by [@davidecavestro](https://github.com/davidecavestro))*

### :wrench: Chores
- [`4d5a6ab`](https://github.com/davidecavestro/dt-xtras/commit/4d5a6aba336ddd93d25d483c8993db9a65ce7870) - pin GH actions *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`208e3b7`](https://github.com/davidecavestro/dt-xtras/commit/208e3b7e75f4c8ee91a27aa05f7f00a41d58ed57) - configure renovate for actions pinning *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`ce2e6b0`](https://github.com/davidecavestro/dt-xtras/commit/ce2e6b0bb0f2d8ea0688cde6c034e4287dd812bb) - use common dialogs *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`5a4e5be`](https://github.com/davidecavestro/dt-xtras/commit/5a4e5be4c76bf526e82f3956faa72d8e43939f35) - update OpenAPI descriptor [skip ci] *(commit by [@github-actions[bot]](https://github.com/apps/github-actions))*
- [`f8d6a3c`](https://github.com/davidecavestro/dt-xtras/commit/f8d6a3c31ebfba0dd9c584cf6e03af8ea7066dd2) - beef up tests for backend *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`7fe07b2`](https://github.com/davidecavestro/dt-xtras/commit/7fe07b25264cf62877d61e88ebd6ce5bac92c920) - increate backend tests coverage *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`b39f75b`](https://github.com/davidecavestro/dt-xtras/commit/b39f75bcff78351c00d74e6628a36b5b884db84c) - use vevn in dv container *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`d232173`](https://github.com/davidecavestro/dt-xtras/commit/d2321738b6efbf370ce7233d2c2965c6335d8fe9) - remove associative for hierarchical *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`ef9cb58`](https://github.com/davidecavestro/dt-xtras/commit/ef9cb582a96e4342684c48ea053c2c07a1a93018) - force renovate PR rebase *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`27abb91`](https://github.com/davidecavestro/dt-xtras/commit/27abb91cb32b36e97d510ecb69ca8b5b0c1eeae9) - expand trees by default *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`6ce89bf`](https://github.com/davidecavestro/dt-xtras/commit/6ce89bf0d41791f56c354b723eb581e9b1699356) - add frontend tests *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`8144ae3`](https://github.com/davidecavestro/dt-xtras/commit/8144ae324976f9ca2a551372b31232f53bcc2a60) - > use nodejs 24 for automations *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`dc0f86c`](https://github.com/davidecavestro/dt-xtras/commit/dc0f86c8ef51acc92362613bd442a734aa4f5ce1) - **deps**: update dependency fastapi to v0.136.1 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`8b529c5`](https://github.com/davidecavestro/dt-xtras/commit/8b529c5795e66988b4cb9024a968ac3a23b81c5e) - **deps**: pin schneegans/dynamic-badges-action action to 0e50b8b *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`fe133a9`](https://github.com/davidecavestro/dt-xtras/commit/fe133a9021ef2606f9302cdd98b2c9a8b9595155) - **deps**: update dependency @tailwindcss/postcss to v4.2.4 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`28775a1`](https://github.com/davidecavestro/dt-xtras/commit/28775a10dff63773aa826c5729b9d5d5a62f46f5) - **deps**: update actions/setup-node digest to 48b55a0 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`8022878`](https://github.com/davidecavestro/dt-xtras/commit/8022878ab8757798344cba7ba1286f017ca02c2b) - **deps**: update dependency @revolist/vue3-datagrid to v4.21.6 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`30b0c28`](https://github.com/davidecavestro/dt-xtras/commit/30b0c2890d3ee6a0e68094e72f1562293a9fc235) - **deps**: update dependency vite to v8.0.10 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`90324db`](https://github.com/davidecavestro/dt-xtras/commit/90324dbdce4a8ac4a96ab8e3b8e2bfbbee6b101c) - update taxonomies example *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`0c07adb`](https://github.com/davidecavestro/dt-xtras/commit/0c07adb930f3eb67b5572d98f97e9d78e3d40d88) - **deps**: update dependency @vitejs/plugin-vue to v6.0.6 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`7d5a189`](https://github.com/davidecavestro/dt-xtras/commit/7d5a1894c9798ec1365b0b54e24378236b241c95) - **deps**: update dependency axios to v1.15.2 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`9f3fcb7`](https://github.com/davidecavestro/dt-xtras/commit/9f3fcb74b2951fb899e4065b2131c80292772219) - **deps**: update dependency python to 3.14 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`b5524a5`](https://github.com/davidecavestro/dt-xtras/commit/b5524a50533da6714ec6852dd7a9b876a1f54e17) - **deps**: update dependency python-multipart to v0.0.26 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`a48c619`](https://github.com/davidecavestro/dt-xtras/commit/a48c619889b0aef7f174fdc75844cd67c8510354) - **deps**: update zizmorcore/zizmor-action action to v0.5.3 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`4e2dab6`](https://github.com/davidecavestro/dt-xtras/commit/4e2dab6bb084936b5149d10baad6f40d4294d57a) - **deps**: update dependency autoprefixer to v10.5.0 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`10fff8d`](https://github.com/davidecavestro/dt-xtras/commit/10fff8d54c7c0498aa705d12243b4b395d5fa6e4) - **deps**: update vitest monorepo to v4 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`0405bdc`](https://github.com/davidecavestro/dt-xtras/commit/0405bdc3e9cd03b153c153b50ec7c38d941d0a67) - **deps**: update dependency regex to v2026 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`2c52b3b`](https://github.com/davidecavestro/dt-xtras/commit/2c52b3bc3f9a6baa863ea476cd200d7d2179a9b2) - **deps**: update dependency tailwindcss to v4 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`9d6ea37`](https://github.com/davidecavestro/dt-xtras/commit/9d6ea379d8de918550a10f3a9419834ade5ccf38) - **deps**: update docker/login-action action to v4 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`f7d4be7`](https://github.com/davidecavestro/dt-xtras/commit/f7d4be7557816b460a1182406213a37fb120a9e8) - **deps**: update postgres docker tag to v18 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`5002871`](https://github.com/davidecavestro/dt-xtras/commit/5002871c2591171c87218b38402fb0154e55bb06) - bump up devcontainer pg to 18 *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`57a570e`](https://github.com/davidecavestro/dt-xtras/commit/57a570eb8e48d26a370444c7c3a2e02bb738568c) - produce coverage for dev *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`6d85570`](https://github.com/davidecavestro/dt-xtras/commit/6d85570da157810afc4ed83dba6c2ffd3df650d4) - explicitly set python interpreter on dev *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`3d63e0a`](https://github.com/davidecavestro/dt-xtras/commit/3d63e0a5c5d698a93cacdd927ee61a9adeca3585) - **deps**: update dependency vue-router to v5.0.6 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`c7c8827`](https://github.com/davidecavestro/dt-xtras/commit/c7c88273bdef2bb5a56fb5903c24c3b010fdf768) - **deps**: update dependency uvicorn to v0.46.0 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`594d058`](https://github.com/davidecavestro/dt-xtras/commit/594d05827b04a3d965df18eacb3231d43f82db14) - **deps**: update dependency pytest to v8.4.2 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`c4467fa`](https://github.com/davidecavestro/dt-xtras/commit/c4467faad97c61b5507ca1753030d20fe6938b0a) - **deps**: update dependency pydantic to v2.13.3 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`a80481c`](https://github.com/davidecavestro/dt-xtras/commit/a80481cbbfed3c2876e0804d6d13362f00e9056c) - **deps**: update aquasecurity/trivy-action action to v0.36.0 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`87873dc`](https://github.com/davidecavestro/dt-xtras/commit/87873dc8b2b40eeeefa149cc292fd0fcc0f27d7f) - beef frontend tests *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`cbab2ed`](https://github.com/davidecavestro/dt-xtras/commit/cbab2ed97ce23a158954bfdee4b9106f4eff78f9) - **deps**: update requarks/changelog-action digest to b78a335 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`3985ac9`](https://github.com/davidecavestro/dt-xtras/commit/3985ac9b0a035584f83efea335ff851c635346aa) - add frontend tests *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`289ef63`](https://github.com/davidecavestro/dt-xtras/commit/289ef639c728d20c87dd882b0b408cb94c3a56d4) - **deps**: update actions/upload-artifact action to v7 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`1239218`](https://github.com/davidecavestro/dt-xtras/commit/12392182830e94ea070f667737d5942c152d2a69) - compact project deck info *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`23299b5`](https://github.com/davidecavestro/dt-xtras/commit/23299b5d1a2f9abb08f01f97535ebac12a797ec5) - show taxonomy name near selected tree node on dashboard *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`fa1bd06`](https://github.com/davidecavestro/dt-xtras/commit/fa1bd06a7ac79df2efed7b0652734b9fc0a3f53c) - **deps**: update dorny/paths-filter action to v4 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`e319efb`](https://github.com/davidecavestro/dt-xtras/commit/e319efb671f847a22ca92f4fb8624921175e04d5) - **deps**: update dependency jsdom to v29 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`f5fc182`](https://github.com/davidecavestro/dt-xtras/commit/f5fc1826a76841b04f700f12811ceefd8ab9b2d0) - **deps**: update dependency python-multipart to v0.0.27 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`c4946e9`](https://github.com/davidecavestro/dt-xtras/commit/c4946e9bdd74683aff1af39c96bbe51ae8c9b1fd) - **deps**: update dependency pytest to v9 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`fb95e7a`](https://github.com/davidecavestro/dt-xtras/commit/fb95e7a2a2805561497606446c5460170d0d974e) - **deps**: update dependency pytest-asyncio to v1 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`238ffb8`](https://github.com/davidecavestro/dt-xtras/commit/238ffb8795976fb88e3991a2c19c95fcab5c9f5f) - **deps**: update dependency respx to v0.23.1 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`7873297`](https://github.com/davidecavestro/dt-xtras/commit/7873297ab0798170cb909740beb4bc56f654e046) - **deps**: update dependency cytoscape to v3.33.3 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`488e841`](https://github.com/davidecavestro/dt-xtras/commit/488e841e67a72bdd2e790f1d467103a86be706ba) - **deps**: update dependency @vue/test-utils to v2.4.9 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`f318c81`](https://github.com/davidecavestro/dt-xtras/commit/f318c817d65b28cd00d3fece91d49f55cb4b7603) - **deps**: update dependency pytest-cov to v7 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`756b715`](https://github.com/davidecavestro/dt-xtras/commit/756b71574a117e2cc8d32ebd1892de883e1836bb) - **deps**: update dependency postcss to v8.5.13 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`e7870e0`](https://github.com/davidecavestro/dt-xtras/commit/e7870e01006ffbec60f88724d20c599e919571b7) - **deps**: update dependency jsdom to v29.1.1 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`c0838f2`](https://github.com/davidecavestro/dt-xtras/commit/c0838f200fcbfc31b81b950d795e2c18aa237000) - compact project decks *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`f26bd3c`](https://github.com/davidecavestro/dt-xtras/commit/f26bd3c6d550ad547099fecef7a821b34ff3f003) - add hints to prj decks *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`cc2b61b`](https://github.com/davidecavestro/dt-xtras/commit/cc2b61b27da43209d3e933130c160f86e97f4b5d) - better project list item organization *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`432f70d`](https://github.com/davidecavestro/dt-xtras/commit/432f70da9abb1b3e5f9417420ea2836e82e916cd) - reorganize project data on TAgs Graph *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`f38359e`](https://github.com/davidecavestro/dt-xtras/commit/f38359eec19f47fbc048744e6ef573ea9d843791) - **deps**: update dependency @vue/test-utils to v2.4.10 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`4eeef46`](https://github.com/davidecavestro/dt-xtras/commit/4eeef46cd2eaed12eb463e5742db2b8504a6a978) - **deps**: update github/codeql-action digest to e46ed2c *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`a81745c`](https://github.com/davidecavestro/dt-xtras/commit/a81745c80663e6e8257861704c55f8f16368609a) - simplify Raw mode for Tags Graph *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`c24aa3c`](https://github.com/davidecavestro/dt-xtras/commit/c24aa3c6ceb6d516c780bebedb57dcaa20ffa29a) - **deps**: update dependency axios to v1.16.0 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`af3b87c`](https://github.com/davidecavestro/dt-xtras/commit/af3b87c7e01971d99189828c4fc8679ec9b18fc6) - disablebuttons in Bulk Project Actions *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`f1b2f2a`](https://github.com/davidecavestro/dt-xtras/commit/f1b2f2a4bbd96cecd969bf4497f72778cacb723c) - use fixed toolbar for project bulk actions *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`f844f7c`](https://github.com/davidecavestro/dt-xtras/commit/f844f7c2490e9f5835eca345fd17222bfa1b4294) - increase test coverage *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`f341423`](https://github.com/davidecavestro/dt-xtras/commit/f341423de4c9e5b529dcebd79600c4aff7b54bc9) - provide uniform api from services *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`3035d2a`](https://github.com/davidecavestro/dt-xtras/commit/3035d2aea067c6b6278d433ff0cf7c36ad3e906f) - beef up tests *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`e5859b2`](https://github.com/davidecavestro/dt-xtras/commit/e5859b2cef399d40f165932ed5aa06898a8d6f15) - **deps**: update dependency regex to v2026.5.9 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`a9d3dfc`](https://github.com/davidecavestro/dt-xtras/commit/a9d3dfc32b026ea0d02f3e8ae66fc6eb49d16d48) - **deps**: update dependency types-regex to v2026.5.9.20260518 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`4382ec8`](https://github.com/davidecavestro/dt-xtras/commit/4382ec81407886b17b7f550cdd803e34f1a814a6) - **deps**: update dependency pydantic to v2.13.4 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`b086026`](https://github.com/davidecavestro/dt-xtras/commit/b08602620d3003f108e72f4021d1c4fbf14899c2) - **deps**: update dependency python-multipart to v0.0.29 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`47ee08f`](https://github.com/davidecavestro/dt-xtras/commit/47ee08fcc066cb672ce551fb2b1fc89f5b827dda) - **deps**: update docker/build-push-action digest to f9f3042 *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`388387d`](https://github.com/davidecavestro/dt-xtras/commit/388387d6abd9c94509c1431113a92dc0613546cf) - **deps**: update docker/login-action digest to 650006c *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`d526b8c`](https://github.com/davidecavestro/dt-xtras/commit/d526b8cdc4b6f93d3f86a7c9611d11735923987f) - **deps**: update github/codeql-action digest to 7211b7c *(commit by [@renovate[bot]](https://github.com/apps/renovate))*
- [`cee3228`](https://github.com/davidecavestro/dt-xtras/commit/cee322883dc0f9206b65e44d067213b7992e9646) - loose coupling *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`d369447`](https://github.com/davidecavestro/dt-xtras/commit/d36944730b43f0cee8d7c42698cfd78391419c69) - cosmetic fixes *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`57e1b73`](https://github.com/davidecavestro/dt-xtras/commit/57e1b731355fa52a18c6306ea2e90033406bade7) - readd data grid *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [v0.8] - 2026-04-16
### :bug: Bug Fixes
- [`3c1e3dd`](https://github.com/davidecavestro/dt-xtras/commit/3c1e3ddd5cce155610820035cebb147688620b84) - broken tag rename *(commit by [@davidecavestro](https://github.com/davidecavestro))*

### :wrench: Chores
- [`d64ec72`](https://github.com/davidecavestro/dt-xtras/commit/d64ec7227ec650e6ff31d83bfcdefd9a0d8b0d0e) - add zizmor for CI checks *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`901b7a0`](https://github.com/davidecavestro/dt-xtras/commit/901b7a0c9d315ccf6ac7be4b3cad61cfc5edd8bd) - switch to alpine to reduce CVEs *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`dc9a7be`](https://github.com/davidecavestro/dt-xtras/commit/dc9a7be0fbd25db308d5542a8aec458126b870a7) - move tree build logic to backend *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [v0.7] - 2026-04-12
### :sparkles: New Features
- [`ef11aef`](https://github.com/davidecavestro/dt-xtras/commit/ef11aef94f7b42765c3692a7cd49127846435114) - enhance bulk tag actions easing selections *(commit by [@davidecavestro](https://github.com/davidecavestro))*

### :bug: Bug Fixes
- [`a0a47ac`](https://github.com/davidecavestro/dt-xtras/commit/a0a47acf2e2a996fec04238e3d45bfc5fc6aa0fd) - broken tag edit *(commit by [@davidecavestro](https://github.com/davidecavestro))*

### :wrench: Chores
- [`d6565a5`](https://github.com/davidecavestro/dt-xtras/commit/d6565a598e7f9c42c0a338565a39899b50fefc0b) - decorate linking/unlinking tags on the Tag Bulk Actions view *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`1e7fbb3`](https://github.com/davidecavestro/dt-xtras/commit/1e7fbb30303d82d4c41dde434c16e25d9c491f1c) - fix tag filtering *(commit by [@davidecavestro](https://github.com/davidecavestro))*


## [v0.6] - 2026-04-11
### :sparkles: New Features
- [`efbde9d`](https://github.com/davidecavestro/dt-xtras/commit/efbde9d79cc31f2e64819781fc55648c6e8c875a) - move the graph logic to backend api *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`ec4125d`](https://github.com/davidecavestro/dt-xtras/commit/ec4125d82337a8a17876cb9bf576744596346906) - use stores for dashboard *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`18dca36`](https://github.com/davidecavestro/dt-xtras/commit/18dca36b4edc2422d951a08e6d9c6fd338284288) - ease creting taxonomy relations *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`56023a4`](https://github.com/davidecavestro/dt-xtras/commit/56023a4e9f95700ff68cf2f5cdabe935c69cc3e9) - show all tags into the navigation tree *(commit by [@davidecavestro](https://github.com/davidecavestro))*

### :bug: Bug Fixes
- [`e528546`](https://github.com/davidecavestro/dt-xtras/commit/e528546e54be919c0623a1350909d6cce3979a9e) - Tag graph not rendering related proejcts *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`30861c2`](https://github.com/davidecavestro/dt-xtras/commit/30861c27207ff1432206e0814c01d842cd02a59f) - edit/create tag dropdowns are broken *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`1b3e6c7`](https://github.com/davidecavestro/dt-xtras/commit/1b3e6c72d5340a08cbed3d15b35a0b2ebe6eec8e) - broken data loading for dashboard *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`b0edc29`](https://github.com/davidecavestro/dt-xtras/commit/b0edc29540e28971d60e0368a6e5b756bcd4f6b8) - the tag bulk actions are broken *(commit by [@davidecavestro](https://github.com/davidecavestro))*

### :wrench: Chores
- [`479adcf`](https://github.com/davidecavestro/dt-xtras/commit/479adcf59620fe9c0274e4c6b5d3a17675b3d92a) - move graph logic to backend refactor wip *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`454807a`](https://github.com/davidecavestro/dt-xtras/commit/454807a8feca941aab9a918a3037150bf3bb17de) - use stores for all frontend *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`9a4478f`](https://github.com/davidecavestro/dt-xtras/commit/9a4478fe6a29bf76a016fc20f9b2e5581a3285f2) - merge graph refactor to master [no ci] *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`1d72b20`](https://github.com/davidecavestro/dt-xtras/commit/1d72b208cdd0bcf7bcf19f8e7b15fd17f14c0ab1) - bump up deps *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`2d985cd`](https://github.com/davidecavestro/dt-xtras/commit/2d985cd016fee379c77d4572659bb132cf35c001) - use proper logging *(commit by [@davidecavestro](https://github.com/davidecavestro))*
- [`e18927d`](https://github.com/davidecavestro/dt-xtras/commit/e18927d8040fa65fa39a9c88c6406ae89b900d46) - remove duplicated logic from frontend *(commit by [@davidecavestro](https://github.com/davidecavestro))*

[v0.6]: https://github.com/davidecavestro/dt-xtras/compare/v0.5...v0.6
[v0.7]: https://github.com/davidecavestro/dt-xtras/compare/v0.6...v0.7
[v0.8]: https://github.com/davidecavestro/dt-xtras/compare/v0.7...v0.8
[v0.9]: https://github.com/davidecavestro/dt-xtras/compare/v0.8...v0.9
