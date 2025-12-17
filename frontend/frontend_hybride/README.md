# Frontend Hybride - Assistant Medical

Frontend React + Tauri pour l'assistant d'evaluation des cephalees.

## Prerequis

- Node.js 18+
- npm ou yarn
- Rust (pour Tauri) - [Installation Rust](https://www.rust-lang.org/tools/install)

## Installation

### 1. Installer les dependances npm

```bash
cd frontend/frontend_hybride
npm install
```

**Dependances Tauri requises :**
- `@tauri-apps/api` - API principale Tauri
- `@tauri-apps/cli` - CLI Tauri
- `@tauri-apps/plugin-dialog` - Dialogues systeme (sauvegarde fichiers)
- `@tauri-apps/plugin-fs` - Acces au systeme de fichiers

Ces dependances sont declarees dans `package.json` et seront installees automatiquement avec `npm install`.

### 2. Configurer Tauri (si nouveau clone)

Si les plugins Tauri ne fonctionnent pas apres `npm install`, reinstallez-les explicitement :

```bash
npm install @tauri-apps/plugin-dialog @tauri-apps/plugin-fs
```

## Lancement

### Mode developpement (web uniquement)

```bash
npm run dev
```

### Mode Tauri (application desktop)

```bash
npm run tauri
```

## Structure

```
frontend_hybride/
├── src/
│   ├── App.jsx          # Composant principal
│   ├── main.jsx         # Point d'entree React
│   └── App.css          # Styles
├── src-tauri/           # Configuration Tauri (Rust)
├── package.json         # Dependances npm
└── vite.config.js       # Configuration Vite
```

## Problemes frequents

### Erreur "Failed to resolve import @tauri-apps/plugin-dialog"

**Cause :** Les plugins Tauri ne sont pas installes.

**Solution :**
```bash
npm install @tauri-apps/plugin-dialog @tauri-apps/plugin-fs
```

### Erreur de compilation Rust

**Cause :** Rust n'est pas installe ou les plugins Tauri ne sont pas configures cote Rust.

**Solution :**
1. Installer Rust : https://www.rust-lang.org/tools/install
2. Verifier `src-tauri/Cargo.toml` contient les plugins necessaires
