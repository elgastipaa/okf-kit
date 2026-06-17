# Decision

* [Los cross-links son relativos al archivo, no absolutos al bundle](0001-relative-links-over-absolute.md) - Se usan links relativos (../x.md) porque los absolutos (/x.md) rompen en GitHub.
* [Consumo permisivo — solo type es requisito duro](0002-permissive-consumption.md) - Al leer, faltantes/type desconocidos/links rotos NO invalidan el bundle; solo type es obligatorio.
* [kit_version y okf_version son dos versiones distintas](0003-kit-version-vs-okf-version.md) - okf_version versiona el formato; kit_version versiona esta guía+templates+tooling.
* [Sin apps externas; vendor-neutral; solo stdlib en el tooling](0004-vendor-neutral-no-external-apps.md) - OKF es markdown + git; el único extra es un linter Python stdlib-only, sin pip ni apps.
* [El bundle en git es la fuente de verdad, no la memoria de la herramienta](0005-knowledge-as-source-of-truth.md) - La memoria privada de la IA es un atajo personal; la verdad vive en knowledge/ versionado.
* [Este bundle usa un perfil Mixto para documentar el propio kit](0006-dogfood-profile-choice.md) - El kit se documenta a sí mismo combinando carpetas de Código y Wiki (perfil Mixto).
