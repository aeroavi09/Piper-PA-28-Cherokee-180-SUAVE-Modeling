# piper CHEROKEE 180.py

#imports
import os
import sys
import subprocess

#set path to the folder of where i have open vsp SET TO YOUR OWN PATH, this worked for me
vsp_main = r'C:\VSP39'
vsp_engine = r'C:\VSP39\python\openvsp\openvsp'
if os.path.exists(vsp_main):
    os.add_dll_directory(vsp_main)
    if vsp_engine not in sys.path:
        sys.path.insert(0, vsp_engine)
try:
    import _vsp as vsp
    vsp.VSPRenew()
    print("Vsp works")

except Exception as e:
    print(f"VSP Error: {e}")

# General Python Imports
import numpy as np
# Numpy is a commonly used mathematically computing package. It contains many frequently used
# mathematical functions and is faster than native Python, especially when using vectorized
# quantities.
import matplotlib.pyplot as plt
# Matplotlib's pyplot can be used to generate a large variety of plots. Here it is used to create
# visualizations of the aircraft's performance throughout the mission.

# SUAVE Imports
import SUAVE
assert SUAVE.__version__=='2.5.2', 'These tutorials only work with the SUAVE 2.5.2 release'
from SUAVE.Core import Data, Units 
from SUAVE.Methods.Propulsion import propeller_design
from SUAVE.Methods.Geometry.Two_Dimensional.Planform import segment_properties
from SUAVE.Plots.Performance import *

from SUAVE.Input_Output.OpenVSP import write, get_vsp_measurements
from SUAVE.Input_Output.OpenVSP.vsp_read import vsp_read

#from SUAVE.Methods.Geometry.Two_Dimensional.Planform import process_main_wing_geometry as process_wing

from SUAVE.Plots.Geometry import plot_vehicle

from copy import deepcopy

output_name = "piper cherokee 180 .vsp3" #name of file in openvsp
plane_name = 'Piper Cherokee 180 '

def main():
    
    vehicle = vehicle_setup()
    
    vsp_write_read(vehicle)
    
    plot_vehicle(vehicle)
    
    # Setup analyses and mission
    analyses = base_analysis(vehicle)
    analyses.finalize()
    mission  = mission_setup(analyses,vehicle)
    
    # evaluate
    results = mission.evaluate()
    
    plot_mission(results)
    
    return

def vehicle_setup():
    
    vehicle                                     = SUAVE.Vehicle() 
    vehicle.tag                                 = plane_name 
    
    #Vehicle level properties
    
    #this is the fuel and mass stuff
    vehicle.mass_properties.max_takeoff         = 2400 * Units.pounds
    vehicle.mass_properties.takeoff             = 2400 * Units.pounds
    vehicle.mass_properties.max_zero_fuel       = 1310 * Units.pounds
    
    #maximum g-load, based on FAA regulations for civil aircraft regulations
    vehicle.envelope.ultimate_load              = 5.7
    vehicle.envelope.limit_load                 = 3.8
    
    #wing area and number of passengers
    vehicle.reference_area                      = 160 * Units.feet**2
    vehicle.passengers                          = 4
    
    #main wing
    
    wing                                        = SUAVE.Components.Wings.Main_Wing() 
    wing.tag                                    = 'main_wing' 
    wing.sweeps.quarter_chord                   = 0.0 * Units.deg
    wing.thickness_to_chord                     = 0.15
    wing.areas.reference                        = 160 * Units.feet**2
    wing.spans.projected                        = 30 * Units.feet
    wing.chords.root                            = 75 * Units.inches
    wing.chords.tip                             = 63 * Units.inches
    wing.taper                                  = wing.chords.tip/wing.chords.root 
    wing.aspect_ratio                           = wing.spans.projected **2 / wing.areas.reference 
    wing.twists.root                            = 0.0 * Units.degrees
    wing.twists.tip                             = 0.0 * Units.degrees
    wing.origin                                 = [[4.809 * Units.feet, 1.832 * Units.feet, -1.145 * Units.feet]] #x,y,z
    wing.vertical                               = False
    wing.symmetric                              = True
    wing.high_lift                              = False
    wing.dynamic_pressure_ratio                 = 1.0
    
    # wing segments ------------
    
    #root
    segment                                     = SUAVE.Components.Wings.Segment()
    segment.tag                                 = 'root' 
    segment.percent_span_location               = 0.0
    segment.twist                               = 0.0 * Units.deg
    segment.root_chord_percent                  = 1.0
    segment.thickness_to_chord                  = 0.15
    segment.dihedral_outboard                   = 6.08233 * Units.deg
    segment.sweeps.quarter_chord                = 26.565 * Units.deg
    wing.append_segment(segment) #repeatable
    
    #break
    segment                                     = SUAVE.Components.Wings.Segment()
    segment.tag                                 = 'break' 
    segment.percent_span_location               = 0.1
    segment.twist                               = 0.0 * Units.deg
    segment.root_chord_percent                  = 0.84
    segment.thickness_to_chord                  = 0.15
    segment.dihedral_outboard                   = 6.08233 * Units.deg
    segment.sweeps.quarter_chord                = 0.0 * Units.deg
    wing.append_segment(segment) #repeatable
    
    #tip
    segment                                     = SUAVE.Components.Wings.Segment()
    segment.tag                                 = 'tip' 
    segment.percent_span_location               = 1.0
    segment.twist                               = 0.0 * Units.deg
    segment.root_chord_percent                  = 0.84
    segment.thickness_to_chord                  = 0.15
    segment.dihedral_outboard                   = 6.08233 * Units.deg
    segment.sweeps.quarter_chord                = 26.565 * Units.deg
    wing.append_segment(segment) 
    
    #fill out more segments automatically
    wing                                        = segment_properties(wing)
    wing                                        = SUAVE.Methods.Geometry.Two_Dimensional.Planform.wing_planform(wing)
    #SUAVE.Methods.Geometry.Two_Dimensional.Planform.process_main_wing_geometry(wing) #new for SUAVE 2.5.2
    
    vehicle.append_component(wing)
    
    #vertical stabilizer
    
    wing                                        = SUAVE.Components.Wings.Vertical_Tail() 
    wing.tag                                    = 'vertical_stabilizer' 
    wing.sweeps.quarter_chord                   = 30 * Units.deg
    wing.thickness_to_chord                     = 0.08
    wing.areas.reference                        = 11.57 * Units.feet**2
    wing.spans.projected                        = 3.8931292 * Units.feet
    wing.chords.root                            = 4.12326 * Units.feet
    wing.chords.tip                             = 1.83256 * Units.feet
    wing.taper                                  = wing.chords.tip/wing.chords.root 
    wing.aspect_ratio                           = wing.spans.projected **2 / wing.areas.reference 
    wing.twists.root                            = 0.0 * Units.degrees
    wing.twists.tip                             = 0.0 * Units.degrees
    wing.origin                                 = [[18.3256 * Units.feet, 0 * Units.feet, 0.45814 * Units.feet]] #x,y,z
    wing.vertical                               = True
    wing.symmetric                              = False
    wing.t_tail                                 = False
    wing.high_lift                              = False
    wing.dynamic_pressure_ratio                 = 1.0
    
    wing                                        = SUAVE.Methods.Geometry.Two_Dimensional.Planform.wing_planform(wing)
    
    vehicle.append_component(wing)
    
    #horizontal stabilizer
    
    wing                                        = SUAVE.Components.Wings.Horizontal_Tail()
    wing.tag                                    = 'horizontal_stabilizer' 
    wing.sweeps.quarter_chord                   = 0 * Units.deg
    wing.thickness_to_chord                     = 0.1
    wing.areas.reference                        = 25 * Units.feet**2
    wing.spans.projected                        = 10 * Units.feet
    wing.chords.root                            = 30 * Units.inches
    wing.chords.tip                             = 30 * Units.inches
    wing.taper                                  = wing.chords.tip/wing.chords.root 
    wing.aspect_ratio                           = wing.spans.projected **2 / wing.areas.reference 
    wing.twists.root                            = 0.0 * Units.degrees
    wing.twists.tip                             = 0.0 * Units.degrees
    wing.origin                                 = [[20.83969 * Units.feet, 0 * Units.feet, 0 * Units.feet]] #x,y,z
    wing.vertical                               = False
    wing.symmetric                              = True
    wing.high_lift                              = False
    wing.dynamic_pressure_ratio                 = 1.0
    
    wing                                        = SUAVE.Methods.Geometry.Two_Dimensional.Planform.wing_planform(wing)
    
    vehicle.append_component(wing)
    
    #fuselage
    
    fuselage                                    = SUAVE.Components.Fuselages.Fuselage()
    fuselage.tag                                = "fuselage"
    fuselage.number_coach_seats                 = 4
    fuselage.width                              = 3.6641216 * Units.feet
    fuselage.lengths.total                      = 23 * Units.feet + 7.83 * Units.inches
    fuselage.lengths.empennage                  = 13.464 * Units.feet
    fuselage.lengths.cabin                      = 7 * Units.feet + 4 * Units.inches
    fuselage.lengths.structure                  = fuselage.lengths.total - fuselage.lengths.empennage
    fuselage.heights.maximum                    = 3.893 * Units.feet
    fuselage.mass_properties.volume             = .4 * fuselage.lengths.total * (np.pi/4) * fuselage.heights.maximum ** 2 
    fuselage.mass_properties.intenal_volume     = .3 * fuselage.lengths.total * (np.pi/4) * fuselage.heights.maximum ** 2 
    fuselage.areas.wetted                       = 20
    fuselage.seats_abreast                      = 2
    fuselage.seat_pitch                         = 30 * Units.inches
    fuselage.fineness.tail                      = 3.0967
    fuselage.fineness.nose                      = 1.3125
    fuselage.lengths.nose                       = 4.809 * Units.feet
    fuselage.heights.at_quarter_length          = 3.435 * Units.feet  
    fuselage.heights.at_three_quarter_length    = 2.29 * Units.feet
    fuselage.heights.at_wing_root_quarter_chord = 3.664 * Units.feet
    fuselage.areas.front_projects               = fuselage.width * fuselage.heights.maximum
    fuselage.effective_diameter                 = 3.664 * Units.feet
    
    #Segment, nose
    segment                                     = SUAVE.Components.Lofted_Body_Segment.Segment()
    segment.tag                                 = "segment_0"
    segment.percent_x_location                  = 0
    segment.percent_z_location                  = 0
    segment.height                              = 0 * Units.feet
    segment.width                               = 0 * Units.feet
    fuselage.Segments.append(segment)
    
    #Segment nose end
    segment                                     = SUAVE.Components.Lofted_Body_Segment.Segment()
    segment.tag                                 = "segment_1"
    segment.percent_x_location                  = 0.0485
    segment.percent_z_location                  = 0
    segment.height                              = 1.145 * Units.feet
    segment.width                               = 1.145 * Units.feet
    fuselage.Segments.append(segment)
    
    #Segment fuselage start
    segment                                     = SUAVE.Components.Lofted_Body_Segment.Segment()
    segment.tag                                 = "segment_2"
    segment.percent_x_location                  = 0.0525
    segment.percent_z_location                  = 0
    segment.height                              = 1.145 * Units.feet
    segment.width                               = 2.2519 * Units.feet
    fuselage.Segments.append(segment)
    
    #Segment
    segment                                     = SUAVE.Components.Lofted_Body_Segment.Segment()
    segment.tag                                 = "segment_3"
    segment.percent_x_location                  = 0.097
    segment.percent_z_location                  = -0.015
    segment.height                              = 2.061* Units.feet
    segment.width                               = 3.664 * Units.feet
    fuselage.Segments.append(segment)
    
    #Segment
    segment                                     = SUAVE.Components.Lofted_Body_Segment.Segment()
    segment.tag                                 = "segment_4"
    segment.percent_x_location                  = 0.206
    segment.percent_z_location                  = -0.0153
    segment.height                              = 2.519* Units.feet
    segment.width                               = 3.664 * Units.feet
    fuselage.Segments.append(segment)
    
    #Segment
    segment                                     = SUAVE.Components.Lofted_Body_Segment.Segment()
    segment.tag                                 = "segment_5"
    segment.percent_x_location                  = 0.2886
    segment.percent_z_location                  = 0.0103
    segment.height                              = 3.893* Units.feet
    segment.width                               = 3.664 * Units.feet
    fuselage.Segments.append(segment)
    
    #Segment
    segment                                     = SUAVE.Components.Lofted_Body_Segment.Segment()
    segment.tag                                 = "segment_6"
    segment.percent_x_location                  = 0.494
    segment.percent_z_location                  = 0.0103
    segment.height                              = 3.664* Units.feet
    segment.width                               = 3.664 * Units.feet
    fuselage.Segments.append(segment)
    
    #Segment
    segment                                     = SUAVE.Components.Lofted_Body_Segment.Segment()
    segment.tag                                 = "segment_6"
    segment.percent_x_location                  = 0.587
    segment.percent_z_location                  = 0.0103
    segment.height                              = 3.206* Units.feet
    segment.width                               = 2.977 * Units.feet
    fuselage.Segments.append(segment)
    
    #Segment
    segment                                     = SUAVE.Components.Lofted_Body_Segment.Segment() 
    segment.tag                                 = "segment_7"
    segment.percent_x_location                  = 1
    segment.percent_z_location                  = 0
    segment.height                              = 0.916* Units.feet
    segment.width                               = 0 * Units.feet
    fuselage.Segments.append(segment)
    
    vehicle.append_component(fuselage)
    
    #engine network
    
    # build network
    net                                         = SUAVE.Components.Energy.Networks.Internal_Combustion_Propeller() 
    net.tag                                     = 'internal_combustion' #name of file in openvsp
    net.number_of_engines                       = 1
    net.identical_propellers                    = True
    
    #the engine is set here
    engine                                      = SUAVE.Components.Energy.Converters.Internal_Combustion_Engine()
    engine.sea_level_power                      = 180 * Units.horsepower
    engine.flat_rate_altitude                   = 0 * Units.feet
    engine.rated_speed                          = 2700 * Units.rpm
    engine.power_specific_fuel_consumption      = 0.5 
    net.engines.append(engine)
    
    #making the prop
    prop                                        = SUAVE.Components.Energy.Converters.Propeller()
    prop.number_of_blades                       = 2
    prop.origin                                 = [[5  * Units.inches, 0, 0]]
    prop.freestream_velocity                    = 141 * Units.mph
    prop.angular_velocity                       = 2620 * Units.rpm
    prop.tip_radius                             = 38 * Units.inches
    prop.hub_radius                             = 4 * Units.inches
    prop.design_Cl                              = 0.6
    prop.design_power                           = .75 * engine.sea_level_power
    prop.design_altitude                        = 9300 * Units.feet
    prop.variable_pitch                         = False
    
    prop.airfoil_geometry = ['./Airfoils/NACA_4412.txt']
    
    # find polars to make the proper geometry
    prop.airfoil_polars = [[
        './Airfoils/Polars/NACA_4412_polar_Re_50000.txt',
        './Airfoils/Polars/NACA_4412_polar_Re_100000.txt',
        './Airfoils/Polars/NACA_4412_polar_Re_200000.txt',
        './Airfoils/Polars/NACA_4412_polar_Re_500000.txt',
        './Airfoils/Polars/NACA_4412_polar_Re_1000000.txt' ]]
    
    prop.airfoil_polar_stations = [0] * 20 
    
    prop = propeller_design(prop)
    
    
    net.propellers.append(prop)
    
    vehicle.append_component(net)
    
    return vehicle

def configs_setup(vehicle):
    #   Initialize Configurations
    configs                                                    = SUAVE.Components.Configs.Config.Container() 
    base_config                                                = SUAVE.Components.Configs.Config(vehicle)
    base_config.tag                                            = 'base'
    configs.append(base_config)
    
    #   Cruise Configuration
    config                                                     = SUAVE.Components.Configs.Config(base_config)
    config.tag                                                 = 'cruise' 
    configs.append(config)

    return configs



def mission_setup(analyses,vehicle): #repeatable
    #   Define the Mission

    #   Initialize the Mission

    mission = SUAVE.Analyses.Mission.Sequential_Segments()
    mission.tag = 'the_mission'


    # unpack Segments module
    Segments = SUAVE.Analyses.Mission.Segments

    # base segment
    base_segment = Segments.Segment()
    

    #   Cruise Segment

    segment = Segments.Cruise.Constant_Speed_Constant_Altitude(base_segment)
    segment.tag = "cruise"

    segment.analyses.extend( analyses )

    segment.altitude  = 9000. * Units.feet
    segment.air_speed = 116.   * Units.knots
    segment.distance  = 100 * Units.nautical_mile
    
    ones_row                                        = segment.state.ones_row   
    segment.state.numerics.number_control_points    = 16
    segment.state.unknowns.throttle                 = 1.0 * ones_row(1)
    segment = vehicle.networks.internal_combustion.add_unknowns_and_residuals_to_segment(segment,rpm=2600)
    
    
    segment.process.iterate.conditions.stability    = SUAVE.Methods.skip
    segment.process.finalize.post_process.stability = SUAVE.Methods.skip    

    # add to mission
    mission.append_segment(segment)


    return mission


def base_analysis(vehicle):

    #   Initialize analying    
    analyses = SUAVE.Analyses.Vehicle()

    ##  Basic Geometry Relations
    sizing = SUAVE.Analyses.Sizing.Sizing()
    sizing.features.vehicle = vehicle
    analyses.append(sizing)

    #  Weights
    weights = SUAVE.Analyses.Weights.Weights_Transport()
    weights.vehicle = vehicle
    analyses.append(weights)

    #  Aerodynamics Analysis
    
    # landing gear drag
    
    main_wheel_width  = 4. * Units.inches
    main_wheel_height = 12. * Units.inches
    nose_gear_height  = 10. * Units.inches
    nose_gear_width   = 4. * Units.inches
    
    total_wheel       = 2*main_wheel_width*main_wheel_height + nose_gear_width*nose_gear_height
    
    main_gear_strut_height = 2. * Units.inches
    main_gear_strut_length = 24. * Units.inches
    nose_gear_strut_height = 12. * Units.inches
    nose_gear_strut_width  = 2. * Units.inches
    
    total_strut = 2*main_gear_strut_height*main_gear_strut_length + nose_gear_strut_height*nose_gear_strut_width
    
    # total drag from extra wheels
    drag_area = 1.4*( total_wheel + total_strut)
    
    
    aerodynamics = SUAVE.Analyses.Aerodynamics.Fidelity_Zero() 
    aerodynamics.geometry                            = vehicle
    aerodynamics.settings.drag_coefficient_increment = 1.0*drag_area/vehicle.reference_area
    analyses.append(aerodynamics)

    # ------------------------------------------------------------------
    #  Energy
    energy= SUAVE.Analyses.Energy.Energy()
    energy.network = vehicle.networks #what is called throughout the mission (at every time step))
    analyses.append(energy)

    # ------------------------------------------------------------------
    #  Planet Analysis
    planet = SUAVE.Analyses.Planets.Planet()
    analyses.append(planet)

    # ------------------------------------------------------------------
    #  Atmosphere Analysis
    atmosphere = SUAVE.Analyses.Atmospheric.US_Standard_1976()
    atmosphere.features.planet = planet.features
    analyses.append(atmosphere)   

    # done!
    return analyses



# ----------------------------------------------------------------------
#   Plot Mission
# ----------------------------------------------------------------------

def plot_mission(results,line_style='bo-'):
    
    # Plot Flight Conditions 
    plot_flight_conditions(results, line_style)
    
    # Plot Aerodynamic Forces 
    plot_aerodynamic_forces(results, line_style)
    
    # Plot Aerodynamic Coefficients 
    plot_aerodynamic_coefficients(results, line_style)
    
    # Drag Components
    plot_drag_components(results, line_style)
    
    # Plot Altitude, sfc, vehicle weight 
    plot_altitude_sfc_weight(results, line_style)
    
    # Plot Velocities 
    plot_aircraft_velocities(results, line_style)  

    return


def vsp_write_read(vehicle):
    
    #save this vehicle
    write(vehicle, plane_name)
    
    
    return


# This section is needed to actually run the various functions in the file
if __name__ == '__main__': 
    main()      

    plt.show()

