### v2.0.0-beta4 -> v2.0.0-rc1

#### Features

 - [`7abd71b`](https://github.com/deis/workflow/commit/7abd71b5a1409e8aa6d0bc738a71eb5e87ed0de9) managing-workflow: add back production deployments
 - [`c8b3548`](https://github.com/deis/workflow/commit/c8b3548979be2a483f6deaf58baa9fe7d197f340) storage: modify docs for configuring storage using env vars
 - [`9e9fc03`](https://github.com/deis/workflow/commit/9e9fc031e96ec757c2747a8d16fd778647512416) customizing-workflow: add component tuning

#### Fixes

 - [`9c14781`](https://github.com/deis/workflow/commit/9c14781df2dfe10f83da2eaefd31be4158f83ca7) production-deployments.md: comment link to non-existent doc
 - [`70221f4`](https://github.com/deis/workflow/commit/70221f4a6aa7020b0cb112a45af7b95a622e6237) users: add broken link

#### Documentation

 - [`539a80c`](https://github.com/deis/workflow/commit/539a80c83b8aabeb85d7c72ca2d1aad0690a5ef5) upgrading-workflow: copy DB creds into new chart
 - [`48c5ea8`](https://github.com/deis/workflow/commit/48c5ea80ae833b95786f872da930776353c49886) upgrading-workflow: require off-cluster storage for upgrade
 - [`ad27e4e`](https://github.com/deis/workflow/commit/ad27e4e65660b395f8aaf3b164ce67558699393d) upgrading-workflow: describe "keeper" upgrade behavior
 - [`9dd5cad`](https://github.com/deis/workflow/commit/9dd5cad0ef9e109e4e582ed4b6c298c4e8768a70) quickstart: add DNS registrar and Route53 docs for AWS
 - [`4e26b54`](https://github.com/deis/workflow/commit/4e26b5485726958bb1a14ad0f7b6632db869a43c) index: move version header to index
 - [`6be97a2`](https://github.com/deis/workflow/commit/6be97a22a851583df44d211d5a105a0799b3eda8) installing-workflow: add docs on dockerbuilder config
 - [`a920428`](https://github.com/deis/workflow/commit/a920428b8a8949781dc52fd257c7c4e5ef2326f3) managing-workflow: remove daemon set warning
 - [`daf12a2`](https://github.com/deis/workflow/commit/daf12a2f9a2488881a8b63a4ea6d43838c01ba87) using-workflow: clarify what username and password reflect
 - [`9c71b3a`](https://github.com/deis/workflow/commit/9c71b3aca2de31f61877943163db650fecf51e2e) release_checklist.md: update with latest deisrel usage
 - [`0d48686`](https://github.com/deis/workflow/commit/0d48686bcfe4f3ac74c29005f117535d533ca35b) release-checklist.md: update with latest processes

#### Maintenance

 - [`079d4d5`](https://github.com/deis/workflow/commit/079d4d55c83635f323321e811dceab14736457b0) src: bump docs to workflow-beta4
 - [`56ead28`](https://github.com/deis/workflow/commit/56ead28e8d2097f978bd1b7000fa3fa90e253c38) sidebar: hide sidebar

### v2.0.0-beta3 -> v2.0.0-beta4

#### Features

 - [`77a924c`](https://github.com/deis/workflow/commit/77a924c14948994c484d38937172e0115d2dba14) monitoring: Add platform-monitoring docs

#### Fixes

 - [`76f4c8f`](https://github.com/deis/workflow/commit/76f4c8ff69edd5e71eb26c764901e9d4ca8c1863) installing-workflow: fix getting started guide links

#### Documentation

 - [`54a251f`](https://github.com/deis/workflow/commit/54a251f0918a3a8abdda7d6427a0d535a62d1162) release-checklist: add minor adjustments and reminder
 - [`e37e5f2`](https://github.com/deis/workflow/commit/e37e5f21a37562f5363f534a64e644d395f87e69) README.md: add slack signup & status badge
 - [`9ca4973`](https://github.com/deis/workflow/commit/9ca4973dc0db386cbe7196da41a64a13d3c21a86) release-checklist: note that milestones should be closed
 - [`c702592`](https://github.com/deis/workflow/commit/c702592383efff8b90a699e9348826e428f42909) CHANGELOG.md: update for v2.0.0-beta3

#### Maintenance

 - [`464bb6d`](https://github.com/deis/workflow/commit/464bb6d1591c28b6d26b7d8c7744e87d6bd1775b) release: add a new removal step for release-checklist
 - [`5c78f72`](https://github.com/deis/workflow/commit/5c78f72bc0e7dc4d3f84aec4ed8ad52f5c8696a6) src: bump documentation to reference v2.0.0-beta3

### v2.0.0-beta2 -> v2.0.0-beta3

#### Features

 - [`5e6c6d0`](https://github.com/deis/workflow/commit/5e6c6d0e559d1c973352a46c8388d485500cb1a2) registry: add private registry documentation
 - [`b4f6a60`](https://github.com/deis/workflow/commit/b4f6a60ac6d77448af1a9e0a5ae9370d2b697c69) managing-workflow: add back operational tasks
 - [`573e7fb`](https://github.com/deis/workflow/commit/573e7fb76e1f8d1189da27725dd356f3a47a3b2b) installing-workflow: add ELB install notes

#### Fixes

 - [`30f0c80`](https://github.com/deis/workflow/commit/30f0c8046b28f546312e88bf53b8180bae3dae81) docs: move releasing.md to roadmap
 - [`e2a883b`](https://github.com/deis/workflow/commit/e2a883bec706da14fa6e426e52bbaa61681150e8) installing-workflow: bump requirement to kubernetes 1.2
 - [`6c09567`](https://github.com/deis/workflow/commit/6c0956728ec5a8ff19e96714fd8893b0f839aa97) themes: fix up navigation on readthedocs

#### Documentation

 - [`efd6ba6`](https://github.com/deis/workflow/commit/efd6ba675b82d31ce0d509921d533d46b0e496b6) (all): improve grammar and fix typos
 - [`41ce729`](https://github.com/deis/workflow/commit/41ce729fca32cc003713c959311b2e7117deac8a) release-checklist: set DEBUG=false in manifests
 - [`6c65793`](https://github.com/deis/workflow/commit/6c6579347c7509d7870f1990e291bf01c12030a0) using-docker-images: add --no-remote

#### Maintenance

 - [`7d2987a`](https://github.com/deis/workflow/commit/7d2987a49c8245a618c99af1393af91f424bdb01) logging: Update to reflect logger being in mainline workflow
 - [`1899594`](https://github.com/deis/workflow/commit/18995945ded724e69149f8cedebb1dbe70e54daa) release: add communication steps to release process

### v2.0.0-beta1 -> v2.0.0-beta2

#### Features

 - [`d555f3a`](https://github.com/deis/workflow/commit/d555f3a81cae17a7537766686c428a4358740e7a) storage: change docs to use deis-object-storage-secret for configuring database
 - [`abd3279`](https://github.com/deis/workflow/commit/abd32796e908f8b71629a373a8b5a05e198cf156) managing-deis: lazy pass at upgrading workflow
 - [`7a32ce8`](https://github.com/deis/workflow/commit/7a32ce826713980e13476c7b5e840635e350d09b) healthchecks: improve healthcheck documentation, add new options and include defaults
 - [`c71b596`](https://github.com/deis/workflow/commit/c71b596ab44bb26c7e1a84f13fb3bcb3050243c0) mkdocs: enable toc extension
 - [`614a487`](https://github.com/deis/workflow/commit/614a487936b41aea2f288bf656b9f5fa9eee7009) docker: add .dockerignore
 - [`5652eef`](https://github.com/deis/workflow/commit/5652eeff2643387f204eff93fadc34982a97b165) storage: change docs to use deis-object-storage-secret for configuring the storage

#### Fixes

 - [`9cd65e6`](https://github.com/deis/workflow/commit/9cd65e65972a98c515b28218f3e2d454206fb751) CONTRIBUTING: fix broken links
