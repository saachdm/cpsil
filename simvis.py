import dearpygui.dearpygui as dpg
import math
class sim_visualization_data():

    def __init__(self,sim_obj):
        self.sim_obj=sim_obj
        with dpg.window(label="CPysil",tag="Controller"):
            with dpg.theme(tag="button_theme"):
                with dpg.theme_component(dpg.mvAll):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (17, 10, 114), category=dpg.mvThemeCat_Core)
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (92, 92, 92), category=dpg.mvThemeCat_Core)
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 120, 0), category=dpg.mvThemeCat_Core)

            dpg.add_button(label="Pause", callback=sim_obj.sim_pause,pos=(10,20),width=120,height=50)
            dpg.add_button(label="Run Simulation", callback=sim_obj.sim_start,pos=(10,100),width=120,height=50)
            dpg.add_slider_float(label="Velocity Reference", callback=sim_obj.set_vref, default_value=sim_obj.vref,
                                min_value=0.0, max_value=20.0, pos=(10, 200), width=300, height=50)
            dpg.add_slider_float(label="Road inclination", callback=sim_obj.set_inclination, default_value=sim_obj.dyn_mod.incline,
                                min_value=-4.0, max_value=4.0, pos=(10, 300), width=300, height=50)
            dpg.add_button(label="Gear +", callback=sim_obj.change_gear,pos=(10,450),width=120,height=50,tag='gearup')
            dpg.add_button(label="Gear -", callback=sim_obj.change_gear,pos=(10,500),width=120,height=50,tag='geardown')
            dpg.bind_item_theme("Controller", "button_theme")
            
        with dpg.window(label="CPysil",tag="Plotter",pos=(500,10)):
            data_y = [0.0] * 10000
            data_x = [0.0] * 10000

            with dpg.theme(tag="plot_theme"):
                with dpg.theme_component(dpg.mvScatterSeries):
                    dpg.add_theme_color(dpg.mvPlotCol_Line, (60, 150, 200), category=dpg.mvThemeCat_Plots)
                    dpg.add_theme_style(dpg.mvPlotStyleVar_Marker, dpg.mvPlotMarker_Cross, category=dpg.mvThemeCat_Plots)
                    dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 7, category=dpg.mvThemeCat_Plots)
            with dpg.theme(tag="shadow_theme"):
                with dpg.theme_component(dpg.mvScatterSeries):
                    dpg.add_theme_color(dpg.mvPlotCol_Line, (169, 169, 169), category=dpg.mvThemeCat_Plots)
                    dpg.add_theme_style(dpg.mvPlotStyleVar_Marker, dpg.mvPlotMarker_Cross, category=dpg.mvThemeCat_Plots)
                    dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 4, category=dpg.mvThemeCat_Plots)
                with dpg.theme_component(dpg.mvLineSeries):
                        dpg.add_theme_color(dpg.mvPlotCol_Line, (169, 169, 169), category=dpg.mvThemeCat_Plots)
                        dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 2.0, category=dpg.mvThemeCat_Plots)


            with dpg.plot(label='Velocity (m/s)',height=250,width=500,pos=(10,10)):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis,label="Time (s)",tag="x_axis_1")
                dpg.add_plot_axis(dpg.mvYAxis,label="m/s",tag="y_axis_1")
                dpg.add_line_series(data_x,data_y, label="velocity", parent="y_axis_1", tag="v_plotline")
                dpg.add_line_series(data_x,data_y, label="velocity_ref", parent="y_axis_1", tag="vref_plotline")
                
            with dpg.plot(label='Inputs',height=250,width=500,pos=(10,250)):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis,label="Time (s)",tag="x_axis_2")
                dpg.add_plot_axis(dpg.mvYAxis,label="-",tag="y_axis_2")
                dpg.add_line_series(data_x,data_y, label="Prop input", parent="y_axis_2", tag="u1_plotline")
                dpg.add_line_series(data_x,data_y, label="Brake input", parent="y_axis_2", tag="u2_plotline")
                
            with dpg.plot(label='Vertical forces',height=250,width=500,pos=(10,500)):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis,label="Time (s)",tag="x_axis_3")
                dpg.add_plot_axis(dpg.mvYAxis,label="N",tag="y_axis_3")
                dpg.add_line_series(data_x,data_y, label="Fzf", parent="y_axis_3", tag="Fzf_plotline")
                dpg.add_line_series(data_x,data_y, label="Fzr", parent="y_axis_3", tag="Fzr_plotline")

            with dpg.plot(label='Engine operating point',height=250,width=700,pos=(10,750)):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis,label="RPM",tag="x_axis_4")
                dpg.add_plot_axis(dpg.mvYAxis,label="Torque (Nm)",tag="y_axis_4")
                dpg.add_line_series(data_x,data_y, label="T-w", parent="y_axis_4", tag="T-w_plotline")
                dpg.add_scatter_series([1],[1], label="T-w", parent="y_axis_4", tag="T-w_plotscatter")
                dpg.add_scatter_series([1],[1], label="T-w", parent="y_axis_4", tag="T-w_shadow_plotscatter")
                dpg.bind_item_theme("T-w_plotscatter", "plot_theme")
                dpg.bind_item_theme("T-w_shadow_plotscatter", "shadow_theme")
                dpg.bind_item_theme("T-w_plotline", "shadow_theme")


    def plotting_routine(self):
    
        ##Figure 1 (Velocity)
        dpg.set_value("v_plotline", [list(self.sim_obj.time_arr[-10000:]),list(self.sim_obj.v_arr[-10000:])])
        dpg.set_value("vref_plotline", [list(self.sim_obj.time_arr[-10000:]),list(self.sim_obj.v_ref_arr[-10000:])])
        max_y_value = max(max(self.sim_obj.v_arr),max(self.sim_obj.v_ref_arr))
        upper_limit = math.ceil(max_y_value)+0.05*max_y_value
        dpg.set_axis_limits("y_axis_1", 0, upper_limit)
        dpg.fit_axis_data('x_axis_1')
        
        ## Figure 2 (Inputs)
        dpg.set_value("u1_plotline", [list(self.sim_obj.time_arr[-10000:]),list(self.sim_obj.u1_arr[-10000:])])
        dpg.set_value("u2_plotline", [list(self.sim_obj.time_arr[-10000:]),list(self.sim_obj.u2_arr[-10000:])])
        dpg.set_axis_limits("y_axis_2", -0.2,1.2)
        dpg.fit_axis_data('x_axis_2')
        
        ## Figure 3 (Fz)
        dpg.set_value("Fzf_plotline", [list(self.sim_obj.time_arr[-10000:]),list(self.sim_obj.Fzf_arr[-10000:])])
        dpg.set_value("Fzr_plotline", [list(self.sim_obj.time_arr[-10000:]),list(self.sim_obj.Fzr_arr[-10000:])]) 
        max_y_value = max(max(self.sim_obj.Fzf_arr),max(self.sim_obj.Fzr_arr))
        upper_limit = math.ceil(max_y_value)+0.05*max_y_value
        dpg.set_axis_limits("y_axis_3", 0, upper_limit)
        dpg.fit_axis_data('x_axis_3')

        ## Figure 4 (T-w)
        radps2rpm= lambda radps_list: list(map(lambda rad_per_s: rad_per_s * 60 / (2 * math.pi), radps_list))
        dpg.set_value("T-w_plotscatter", [list(radps2rpm(self.sim_obj.omega_arr[-1:])),list(self.sim_obj.T_arr[-1:])])
        dpg.set_value("T-w_shadow_plotscatter", [list(radps2rpm(self.sim_obj.omega_arr[-5:-1])),list(self.sim_obj.T_arr[-5:-1])])
        dpg.set_value("T-w_plotline", [list(radps2rpm(self.sim_obj.omega_arr[-100:])),list(self.sim_obj.T_arr[-100:])]) 
        dpg.set_axis_limits("x_axis_4", -4000, 4000)
        dpg.set_axis_limits("y_axis_4", -200, 200)
