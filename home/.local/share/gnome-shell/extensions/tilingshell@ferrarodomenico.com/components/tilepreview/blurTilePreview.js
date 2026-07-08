// For GNOME Shell version before 45
const Me = imports.misc.extensionUtils.getCurrentExtension();
var registerGObjectClass = Me.imports.utils.gjs.registerGObjectClass;
var Shell = Me.imports.gi.ext.Shell;
var TilePreview = Me.imports.components.tilepreview.tilePreview.TilePreview;
var _BlurTilePreview = class _BlurTilePreview extends TilePreview {
  _init() {
    super._init();
    const sigma = 36;
    this.add_effect(
      new Shell.BlurEffect({
        // @ts-expect-error "sigma is available"
        sigma,
        // radius: sigma * 2,
        brightness: 1,
        mode: Shell.BlurMode.BACKGROUND
        // blur what is behind the widget
      })
    );
    this.add_style_class_name("blur-tile-preview");
  }
};
registerGObjectClass(_BlurTilePreview);
var BlurTilePreview = _BlurTilePreview;