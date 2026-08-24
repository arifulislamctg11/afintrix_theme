/* Afintrix desk scripts, bundled so esbuild emits a content-hashed filename.
   See the note in afintrix.bundle.css — same cache problem, same fix.
   Each file is a self-contained IIFE; the import order is the load order. */
import "./afintrix_brand.js";
import "./afintrix_theme.js";
import "./afintrix_sidebar.js";
import "./afintrix_topbar.js";
import "./afintrix_kanban.js";
