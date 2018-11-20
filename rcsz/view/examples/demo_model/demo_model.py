'''

Example demonstrating the interaction between model 
and Visualization sheet.

VizSheet time coincides with the Model time.
The model is required to deliver the time range 
by returning the values of time_low, time_high and time_step. 
By default, the model is expected to return 
the time range as (0,1,10). Updates of the model 
time range should be immediately reflected in the VizSheet. 
An update of the range can be done by the user or by the 
calculation changing the value of t within the model. 
The change of the visual time is reported to the VizXD 
adapters that are requested to change their state.

Provide a dummy model delivering the time range and demonstrate 
the case of interactive steering versus separate calculation 
and browsing steps.

The example should be provided in view.examples.time_control.py

Created on Mar 10, 2017

@author: rch
'''

from bmcs.time_functions.tfun_pwl_interactive import TFunPWLInteractive
from ibvpy.api import BCDof
from traits.api import Instance, List,\
    Property, cached_property, Float
from traitsui.api import View, Include, VGroup, UItem, Item
from view.plot2d import Vis2D, Viz2D
from view.window import BMCSWindow
from view.window.bmcs_window import BMCSModel
import matplotlib.patches as patches
from tloop import TimeLoop
from view.examples.demo_model.response_tracer import ResponseTracer
from view.examples.demo_model.tline import TLine


class ShearZoneShapeViz2D(Viz2D):

    def plot(self, ax, vot):
        H = self.vis2d.H
        L = self.vis2d.L

        rect = patches.Rectangle(
            (0, 0), L, H, linewidth=1, edgecolor='r', facecolor='green')

        # Add the patch to the Axes
        ax.add_patch(rect)


class DemoModel(BMCSModel, Vis2D):
    '''Demo model of the BMCS Window

    Shows how the time control within an application of BMCS
    is realized.

    Run mode
    ========
    The model provides the methods for the Actions 
    Run, Pause, and Continue.

    During these actions, values are registered within
    the response tracers. The model can also send an update
    to the visual object time - so that the response tracers
    are asked to be updated.

    Sliding mode
    ============
    Once the calculation is finished, the slider in the VizSheet
    can be used to browse through the viz-adapters and visualize 
    the response for the current vot.

    Interactive mode
    ================
    Boundary condition can be constructed interactively by
    a boundary condition factory. The factory acts as a Run mode.
    '''
    node_name = 'demo model'

    tree_node_list = List

    H = Float(0.3, auto_set=False, enter_set=True)

    L = Float(0.3, auto_set=False, enter_set=True)

    def _tree_node_list_default(self):
        return [self.tline, self.rt, self.bc_dof]

    tline = Instance(TLine)
    '''Time range.
    '''

    def _tline_default(self):
        return TLine(min=0.0, step=0.1, max=0.0,
                     time_change_notifier=self.time_changed,
                     )

    def time_changed(self, time):
        self.ui.viz_sheet.time_changed(time)

    def time_range_changed(self, tmax):
        self.tline.max = tmax
        self.ui.viz_sheet.time_range_changed(tmax)

    def set_tmax(self, time):
        self.time_range_changed(time)

    tloop = Property(Instance(TimeLoop))

    @cached_property
    def _get_tloop(self):
        return TimeLoop(tline=self.tline)

    def eval(self):
        self.tloop.eval()

    rt = Instance(ResponseTracer, ())

    bc_dof = Instance(BCDof)

    def _bc_dof_default(self):
        return BCDof(time_function=TFunPWLInteractive())

    viz2d_classes = {
        'shear_zone': ShearZoneShapeViz2D
    }

    tree_view = View(
        VGroup(
            Include('actions'),
            #            UItem('bc_dof@', height=500),
            Item('H'),
            Item('L')
        )
    )


if __name__ == '__main__':
    model = DemoModel()
    tv = BMCSWindow(model=model)
    model.rt.add_viz2d('time_profile', 'response tracer #1')
    model.add_viz2d('shear_zone', 'shear zone shape')
    tv.configure_traits()
