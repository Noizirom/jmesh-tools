from .shape import *

class Polyline_Shape(Shape):

    def can_close(self):
        return len(self._vertices) > 1

    def close(self):
            
        if self.can_close():
            self.state = ShapeState.CREATED
            return True
            
        return False

    def get_vertices_copy(self, mouse_pos = None):
        result = self._vertices.copy()

        if mouse_pos is not None and self.is_processing():
            result.append(mouse_pos)

        return result

    def is_draw_input(self, context):
        return context.scene.shape_input_method == "Draw"

    def handle_mouse_press(self, mouse_pos_2d, mouse_pos_3d, event, context):

        super().handle_mouse_press(mouse_pos_2d, mouse_pos_3d, event, context)

        if mouse_pos_3d is None:
            return False

        if self.is_draw_input(context) and event.ctrl and self.state == ShapeState.NONE:
            self.state = ShapeState.PROCESSING
            return False

        if self.is_draw_input(context) and event.ctrl and self.state == ShapeState.PROCESSING:
            self.close()
            return False

        if (self.is_none() and event.ctrl) or (self.is_processing() and not event.ctrl):

            self.add_vertex(mouse_pos_3d)
            self._vertices_2d.append(get_2d_vertex(context, mouse_pos_3d))
            self.state = ShapeState.PROCESSING
            return False

        elif self.is_processing() and event.ctrl and self.can_close():
            self.add_vertex(mouse_pos_3d)
            self._vertices_2d.append(get_2d_vertex(context, mouse_pos_3d))
            self.close()
            return False

        elif self.is_created() and event.ctrl:
            return True

        return False

    def handle_mouse_move(self, mouse_pos_2d, mouse_pos_3d, event, context):

        if self.is_draw_input(context):
            if self.state == ShapeState.PROCESSING:
                if len(self._vertices) == 2:
                    self.build_actions()

                self.add_vertex(mouse_pos_3d)
                self._vertices_2d.append(get_2d_vertex(context, mouse_pos_3d))
                return True

        else:
            if self.is_processing():
                return True


        result = super().handle_mouse_move(mouse_pos_2d, mouse_pos_3d, event, context)

        return result

    def get_point_size(self, context):
        if self.is_draw_input(context):
            return 3
        return super().get_point_size(context)

    def build_actions(self):
        super().build_actions()
        bool_mode = bpy.context.scene.bool_mode
        input_method = bpy.context.scene.shape_input_method

        self.add_action(Action(self.get_prim_id(),  "Primitive",          "Polyline"),   None)
        self.add_action(Action("O",                 "Operation",          bool_mode),    None)
        self.add_action(Action("I",                 "Input",       input_method), None)
        self.build_move_action()
        self.build_extrude_action()

        if not self.is_draw_input(bpy.context):
            self.add_action(Action("Left Click",    "Add line",           ""),          ShapeState.PROCESSING)
        else:
            self.add_action(Action("Move mouse",    "Draw",               ""),          ShapeState.PROCESSING)  

        self.add_action(Action("Ctrl + Left Click", "Start",              ""),          ShapeState.NONE)

        if self.can_close():
            self.add_action(Action("Ctrl + Left Click", "Complete shape",    ""),          ShapeState.PROCESSING)

        self.add_action(Action("Ctrl + Left Click", "Apply",              ""),          ShapeState.CREATED)
        self.add_action(Action("Left Drag",         "Move points",        ""),          ShapeState.CREATED)
        self.add_action(Action("Esc",               self.get_esc_title(), ""),          None)