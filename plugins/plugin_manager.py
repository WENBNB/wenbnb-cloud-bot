# === LOAD ALL PLUGINS ===
def load_all_plugins(dispatcher):
    """
    WENBNB Plugin Manager v4.1 — Universal Neural Loader
    🧠 Supports both 'register_handlers' (modern) and 'register' (legacy) plugin structures.
    Automatically imports and registers all .py modules in /plugins folder.
    """

    loaded = []
    failed = []

    print("\n🧩 [WENBNB Neural Loader] Initializing modular system...\n")

    for file in os.listdir(PLUGIN_DIR):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]
            try:
                module = importlib.import_module(f"{PLUGIN_DIR}.{module_name}")

                # ✅ New unified registration logic
                if hasattr(module, "register_handlers"):
                    module.register_handlers(dispatcher)
                    ACTIVE_PLUGINS[module_name] = "✅ Active"
                    loaded.append(module_name)
                    print(f"🔹 Loaded: {module_name} (modern)")

                elif hasattr(module, "register"):
                    module.register(dispatcher)
                    ACTIVE_PLUGINS[module_name] = "✅ Active (Legacy)"
                    loaded.append(module_name)
                    print(f"🔸 Loaded: {module_name} (legacy)")

                else:
                    ACTIVE_PLUGINS[module_name] = "⚠️ No Handler"
                    print(f"⚠️ Skipped: {module_name} — No register() or register_handlers() found")

            except Exception as e:
                ACTIVE_PLUGINS[module_name] = f"❌ Error: {e}"
                failed.append((module_name, str(e)))
                print(f"❌ Failed: {module_name} — {e}")

    # === Summary Logging ===
    print("\n🧠 [WENBNB Neural Loader] Summary:")
    print(f"✅ Active Modules: {len(loaded)}")
    if failed:
        print(f"⚠️ Failed to Load: {len(failed)} modules — {failed}")
    else:
        print("🚀 All plugins loaded successfully!")

    print("\n🔹 Loaded List:", loaded)
    print("\n---------------------------------------------\n")

    return loaded, failed
