# Reference

* [SQLite: sqlite_sequence no tiene fila hasta el primer INSERT](codigos-cortos-en-db-nueva.md) - El piso de ids no se aplicaba en una base nueva porque la fila del contador todavía no existía; arreglado, y el test que lo tapaba también.
* [Las flags de entorno y cuáles no hacen nada](flags-de-entorno.md) - De las tres flags que expone el healthcheck, sólo FLAG_ANALYTICS cambia el comportamiento; las otras dos están declaradas y sin uso.
* [Un path con caracteres fuera de base62 revienta el GET](paths-invalidos-rompen-el-get.md) - decode() levanta ValueError ante cualquier carácter que no esté en el alfabeto, así que pedidos como /favicon.ico terminan en error del handler.
