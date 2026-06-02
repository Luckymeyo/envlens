from __future__ import annotations

from pathlib import Path

from .models import EnvSpec

PRESET_SOURCE = Path("<preset>")


def get_preset_specs(names: list[str] | None) -> dict[str, EnvSpec]:
    specs: dict[str, EnvSpec] = {}
    for name in names or []:
        normalized = normalize_preset_name(name)
        for key, spec in PRESETS.get(normalized, {}).items():
            specs.setdefault(key, spec)
    return specs


def normalize_preset_name(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def spec(
    key: str,
    type: str = "string",
    required: bool = False,
    default: str | None = None,
    values: list[str] | None = None,
    description: str = "",
    secret: bool | None = None,
    public: bool | None = None,
) -> EnvSpec:
    return EnvSpec(
        key=key,
        type=type,
        required=required,
        default=default,
        values=values or [],
        description=description,
        secret=secret,
        public=public,
        source=PRESET_SOURCE,
    )


COMMON_NODE = {
    "NODE_ENV": spec(
        "NODE_ENV",
        type="enum",
        values=["development", "test", "production"],
        default="development",
        description="Node.js runtime environment.",
    ),
    "PORT": spec("PORT", type="integer", description="Local server port."),
}

PRESETS: dict[str, dict[str, EnvSpec]] = {
    "nextjs": {
        **COMMON_NODE,
        "NEXT_TELEMETRY_DISABLED": spec(
            "NEXT_TELEMETRY_DISABLED",
            type="boolean",
            description="Disable Next.js anonymous telemetry.",
        ),
        "VERCEL": spec("VERCEL", type="boolean", description="Set by Vercel when running in its platform."),
        "VERCEL_URL": spec("VERCEL_URL", type="string", description="Deployment URL supplied by Vercel."),
    },
    "vite": {
        **COMMON_NODE,
        "MODE": spec("MODE", type="string", description="Vite mode name."),
        "BASE_URL": spec("BASE_URL", type="string", description="Vite public base path."),
        "DEV": spec("DEV", type="boolean", description="Vite development-mode flag."),
        "PROD": spec("PROD", type="boolean", description="Vite production-mode flag."),
        "SSR": spec("SSR", type="boolean", description="Vite server-side-rendering flag."),
    },
    "django": {
        "DJANGO_SETTINGS_MODULE": spec("DJANGO_SETTINGS_MODULE", description="Python path to Django settings."),
        "SECRET_KEY": spec("SECRET_KEY", required=True, secret=True, description="Django signing secret."),
        "DEBUG": spec("DEBUG", type="boolean", description="Django debug mode."),
        "DATABASE_URL": spec("DATABASE_URL", type="url", description="Database connection URL."),
        "ALLOWED_HOSTS": spec("ALLOWED_HOSTS", description="Comma-separated Django host allowlist."),
    },
    "fastapi": {
        "APP_ENV": spec("APP_ENV", description="Application environment name."),
        "DATABASE_URL": spec("DATABASE_URL", type="url", description="Database connection URL."),
        "PORT": spec("PORT", type="integer", description="Local API server port."),
        "HOST": spec("HOST", description="API server bind host."),
    },
    "docker-compose": {
        "COMPOSE_PROJECT_NAME": spec("COMPOSE_PROJECT_NAME", description="Docker Compose project name."),
        "COMPOSE_PROFILES": spec("COMPOSE_PROFILES", description="Comma-separated Docker Compose profiles."),
        "DOCKER_HOST": spec("DOCKER_HOST", description="Docker daemon endpoint."),
        "PORT": spec("PORT", type="integer", description="Service port commonly passed to Compose."),
    },
}

