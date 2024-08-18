import bpy
from bl_ui.generic_ui_list import draw_ui_list
from .operators import ClearSemanticRemapList,PrefillSemanticRemapList, Import3DMigotoFrameAnalysis, Import3DMigotoRaw, Import3DMigotoPose, Export3DMigoto, ApplyVGMap, Export3DMigotoXXMI
class MIGOTO_UL_semantic_remap_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "semantic_from", text="", emboss=False, icon_value=icon)
            if item.InputSlotClass == 'per-instance':
                layout.label(text="Instanced Data")
                layout.enabled = False
            elif item.valid == False:
                layout.label(text="INVALID")
                layout.enabled = False
            else:
                layout.prop(item, "semantic_to", text="", emboss=False, icon_value=icon)
        elif self.layout_type == 'GRID':
            # Doco says we must implement this layout type, but I don't see
            # that it would be particularly useful, and not sure if we actually
            # expect the list to render with this type in practice. Untested.
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class MIGOTO_MT_semantic_remap_menu(bpy.types.Menu):
    bl_label = "Semantic Remap Options"

    def draw(self, context):
        layout = self.layout

        layout.operator(ClearSemanticRemapList.bl_idname)
        layout.operator(PrefillSemanticRemapList.bl_idname)

class MigotoImportOptionsPanelBase(object):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        operator = context.space_data.active_operator
        return operator.bl_idname == "IMPORT_MESH_OT_migoto_frame_analysis"

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False

class MIGOTO_PT_ImportFrameAnalysisMainPanel(MigotoImportOptionsPanelBase, bpy.types.Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    bl_order = 0

    def draw(self, context):
        MigotoImportOptionsPanelBase.draw(self, context)
        operator = context.space_data.active_operator
        self.layout.prop(operator, "flip_texcoord_v")
        self.layout.prop(operator, "flip_winding")
        self.layout.prop(operator, "flip_normal")

class MIGOTO_PT_ImportFrameAnalysisRelatedFilesPanel(MigotoImportOptionsPanelBase, bpy.types.Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    bl_order = 1

    def draw(self, context):
        MigotoImportOptionsPanelBase.draw(self, context)
        operator = context.space_data.active_operator
        self.layout.enabled = not operator.load_buf
        self.layout.prop(operator, "load_related")
        self.layout.prop(operator, "load_related_so_vb")
        self.layout.prop(operator, "merge_meshes")

class MIGOTO_PT_ImportFrameAnalysisBufFilesPanel(MigotoImportOptionsPanelBase, bpy.types.Panel):
    bl_label = "Load .buf files instead"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 2

    def draw_header(self, context):
        operator = context.space_data.active_operator
        self.layout.prop(operator, "load_buf", text="")

    def draw(self, context):
        MigotoImportOptionsPanelBase.draw(self, context)
        operator = context.space_data.active_operator
        self.layout.enabled = operator.load_buf
        self.layout.prop(operator, "load_buf_limit_range")

class MIGOTO_PT_ImportFrameAnalysisBonePanel(MigotoImportOptionsPanelBase, bpy.types.Panel):
    bl_label = ""
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 3

    def draw_header(self, context):
        operator = context.space_data.active_operator
        self.layout.prop(operator, "pose_cb")

    def draw(self, context):
        MigotoImportOptionsPanelBase.draw(self, context)
        operator = context.space_data.active_operator
        self.layout.prop(operator, "pose_cb_off")
        self.layout.prop(operator, "pose_cb_step")
class MIGOTO_PT_ImportFrameAnalysisRemapSemanticsPanel(MigotoImportOptionsPanelBase, bpy.types.Panel):
    bl_label = "Semantic Remap"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_order = 4

    def draw(self, context):
        MigotoImportOptionsPanelBase.draw(self, context)
        operator = context.space_data.active_operator

        # TODO: Add layout.operator() to read selected file and fill in semantics

        if context.path_resolve is None:
            # Avoid exceptions in console - seems like draw() is called several
            # times (not sure why) and sometimes path_resolve isn't available.
            return
        draw_ui_list(self.layout, context,
                class_name='MIGOTO_UL_semantic_remap_list',
                menu_class_name='MIGOTO_MT_semantic_remap_menu',
                list_path='active_operator.properties.semantic_remap',
                active_index_path='active_operator.properties.semantic_remap_idx',
                unique_id='migoto_import_semantic_remap_list',
                item_dyntip_propname='tooltip',
                )

class MIGOTO_PT_ImportFrameAnalysisManualOrientation(MigotoImportOptionsPanelBase, bpy.types.Panel):
    bl_label = "Orientation"
    bl_order = 5

    def draw(self, context):
        MigotoImportOptionsPanelBase.draw(self, context)
        operator = context.space_data.active_operator
        self.layout.prop(operator, "axis_forward")
        self.layout.prop(operator, "axis_up")
class MIGOTO_PT_ImportFrameAnalysisCleanUp(MigotoImportOptionsPanelBase, bpy.types.Panel):
    bl_label = "Clean Up mesh after import"
    bl_order = 6

    def draw(self, context):
        MigotoImportOptionsPanelBase.draw(self, context)
        operator = context.space_data.active_operator
        self.layout.prop(operator, "merge_verts")
        self.layout.prop(operator, "tris_to_quads")
        self.layout.prop(operator, "clean_loose")
class XXMI_PT_Sidebar(bpy.types.Panel):
    '''Main Panel'''
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "XXMI Tools"
    bl_idname = "XXMI_PT_Sidebar"
    bl_label = "XXMI Tools"
    bl_context = "objectmode"

    # def draw_header(self, context):
    #     layout = self.layout
    #     row = layout.row()
    #     row.operator("wm.url_open", text="",icon="QUESTION"
    #                 ).url = "github.com/leotorrez/LeoTools/blob/main/guides/JoinMeshesGuide.md"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        xxmi = context.scene.xxmi
        split = layout.split(factor=0.75)
        col_1 = split.column()
        col_2 = split.column()
        col_1.prop(xxmi, "dump_path")
        col_1.prop(xxmi, "destination_path")
        col_2.operator("dump.selector", icon="FILE_FOLDER", text="")
        col_2.operator("destination.selector", icon="FILE_FOLDER", text="")
        layout.separator()
        col = layout.column(align=True)
        col.prop(xxmi, 'game')
        # draw dropdown panel

        # col.prop(xxmi, 'outline_optimization')
        
        # if xxmi.outline_optimization:
        #     col.prop(xxmi, 'toggle_rounding_outline', text='Vertex Position Rounding', toggle=True, icon="SHADING_WIRE")
        #     col.prop(xxmi, 'decimal_rounding_outline')
        #     if xxmi.toggle_rounding_outline:
        #         col.prop(xxmi, 'detect_edges')
        #     if xxmi.detect_edges and xxmi.toggle_rounding_outline:
        #         col.prop(xxmi, 'nearest_edge_distance')
        #     col.prop(xxmi, 'overlapping_faces')
        #     col.prop(xxmi, 'angle_weighted')
        #     col.prop(xxmi, 'calculate_all_faces')
class XXMISidebarOptionsPanelBase(object):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "XXMI_PT_Sidebar"

    # @classmethod
    # def poll(cls, context):
    #     operator = context.space_data.active_operator
    #     return operator.bl_idname == "XXMI_PT_Sidebar"

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False
class XXMI_PT_SidePanelExportSettings(XXMISidebarOptionsPanelBase, bpy.types.Panel):
    bl_label = "Export Settings"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 0

    # def draw_header(self, context):
    #     xxmi = context.scene.xxmi
    #     self.layout.prop(xxmi, "outline_optimization")

    def draw(self, context):
        XXMISidebarOptionsPanelBase.draw(self, context)
        xxmi = context.scene.xxmi
        col = self.layout.column(align=True)
        col.prop(xxmi, 'flip_winding')
        col.prop(xxmi, 'flip_normal')
        col.prop(xxmi, 'use_foldername')
        col.prop(xxmi, 'ignore_hidden')
        col.prop(xxmi, 'only_selected')
        col.prop(xxmi, 'no_ramps')
        col.prop(xxmi, 'delete_intermediate')
        col.prop(xxmi, 'copy_textures')
class XXMI_PT_SidePanelExportCredit(XXMISidebarOptionsPanelBase, bpy.types.Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    bl_order = 2

    # def draw_header(self, context):
    #     xxmi = context.scene.xxmi
    #     self.layout.prop(xxmi, "outline_optimization")

    def draw(self, context):
        XXMISidebarOptionsPanelBase.draw(self, context)
        xxmi = context.scene.xxmi
        col = self.layout.column(align=True)
        col.prop(xxmi, 'credit')
class XXMI_PT_SidePanelOutline(XXMISidebarOptionsPanelBase, bpy.types.Panel):
    bl_label = ""
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 1

    def draw_header(self, context):
        xxmi = context.scene.xxmi
        self.layout.prop(xxmi, "outline_optimization")

    def draw(self, context):
        XXMISidebarOptionsPanelBase.draw(self, context)
        xxmi = context.scene.xxmi
        self.layout.enabled = xxmi.outline_optimization
        self.layout.prop(xxmi, "toggle_rounding_outline", text='Vertex Position Rounding', toggle=True, icon="SHADING_WIRE")
        self.layout.prop(xxmi, "decimal_rounding_outline")
        if xxmi.toggle_rounding_outline:
            self.layout.prop(xxmi, "detect_edges")
        if xxmi.detect_edges and xxmi.toggle_rounding_outline:
            self.layout.prop(xxmi, "nearest_edge_distance")
        self.layout.prop(xxmi, "overlapping_faces")
        self.layout.prop(xxmi, "angle_weighted")
        self.layout.prop(xxmi, "calculate_all_faces")
class XXMI_PT_SidePanelExport(XXMISidebarOptionsPanelBase, bpy.types.Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    bl_order = 99

    def draw(self, context):
        XXMISidebarOptionsPanelBase.draw(self, context)
        layout = self.layout
        row = layout.row()
        row.operator("xxmi.exportadvanced", text="Export Mod")

def menu_func_import_fa(self, context):
    self.layout.operator(Import3DMigotoFrameAnalysis.bl_idname, text="3DMigoto frame analysis dump (vb.txt + ib.txt)")

def menu_func_import_raw(self, context):
    self.layout.operator(Import3DMigotoRaw.bl_idname, text="3DMigoto raw buffers (.vb + .ib)")

def menu_func_import_pose(self, context):
    self.layout.operator(Import3DMigotoPose.bl_idname, text="3DMigoto pose (.txt)")

def menu_func_export(self, context):
    self.layout.operator(Export3DMigoto.bl_idname, text="3DMigoto raw buffers (.vb + .ib)")

def menu_func_export_xxmi(self, context):
    self.layout.operator(Export3DMigotoXXMI.bl_idname, text="Exports Mod Folder")

def menu_func_apply_vgmap(self, context):
    self.layout.operator(ApplyVGMap.bl_idname, text="Apply 3DMigoto vertex group map to current object (.vgmap)")

import_menu = bpy.types.TOPBAR_MT_file_import
export_menu = bpy.types.TOPBAR_MT_file_export
def register():
    import_menu.append(menu_func_import_fa)
    import_menu.append(menu_func_import_raw)
    export_menu.append(menu_func_export)
    export_menu.append(menu_func_export_xxmi)
    import_menu.append(menu_func_apply_vgmap)
    import_menu.append(menu_func_import_pose)

def unregister():
    import_menu.remove(menu_func_import_fa)
    import_menu.remove(menu_func_import_raw)
    export_menu.remove(menu_func_export)
    export_menu.remove(menu_func_export_xxmi)
    import_menu.remove(menu_func_apply_vgmap)
    import_menu.remove(menu_func_import_pose)