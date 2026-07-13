# Hermes Local Skills Backup

Backup portable de todas las skills instaladas localmente en este perfil de Hermes que **no forman parte del catálogo nativo/bundled**.

- Fuente local: perfil Hermes `default`
- Clasificación: `hermes skills list --source local`
- Total esperado: **38 skills**
- No incluye skills nativas de Hermes.
- No incluye configuración, memoria, sesiones, credenciales ni archivos `.env`.

## Estructura

```text
skills/                 # skills no nativas, conservando categoría y archivos auxiliares
inventory.json          # nombres, rutas y metadatos del respaldo
scripts/install.py      # instala/restaura este respaldo en otro Hermes
scripts/sync_from_hermes.py  # vuelve a copiar las mismas skills desde un perfil local
THIRD_PARTY_NOTICES.md  # licencias y atribuciones detectadas
```

## Restaurar en otro Hermes

```bash
python scripts/install.py
```

El instalador copia cada carpeta bajo el `HERMES_HOME` detectado. En Windows usa por defecto `%LOCALAPPDATA%\\hermes`; en Linux/macOS usa `~/.hermes`. No sobrescribe una skill existente sin `--force`.

```bash
python scripts/install.py --force
```

Después, iniciar una sesión nueva o ejecutar `/reload-skills`.

## Actualizar respaldo

```bash
python scripts/sync_from_hermes.py
```

Solo sincroniza nombres registrados en `inventory.json`; nunca copia skills nativas, credenciales, memoria o configuración.

## Seguridad

Repositorio diseñado como **privado**. Antes de cada publicación se ejecuta escaneo de secretos y datos sensibles. Archivos operativos de Hermes (`.env`, `auth.json`, `config.yaml`, sesiones, memoria) quedan fuera por diseño.

## Licencias

Cada skill conserva su licencia y atribuciones originales cuando existen. Revisar `THIRD_PARTY_NOTICES.md` antes de cambiar visibilidad a pública.
