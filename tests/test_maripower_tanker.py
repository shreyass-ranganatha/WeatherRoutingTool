from datetime import datetime, timedelta
import os

import matplotlib.pyplot as plt
import numpy as np
import pytest
import xarray as xr
from astropy import units as u

import tests.basic_test_func as basic_test_func
import WeatherRoutingTool.utils.unit_conversion as utils
from WeatherRoutingTool.routeparams import RouteParams

have_maripower = False
try:
    import mariPower
    from WeatherRoutingTool.ship.maripower_tanker import MariPowerTanker

    have_maripower = True
except ModuleNotFoundError:
    pass  # maripower installation is optional


@pytest.mark.skip(reason="maripower needs adjustments for Python 3.11.")
# @pytest.mark.skipif(not have_maripower, reason="maripower is not installed")
@pytest.mark.maripower
class TestMariPowerTanker:
    def compare_times(self, time64, time):
        time64 = (time64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        time = (time - datetime(1970, 1, 1, 0, 0))
        for iTime in range(0, time.shape[0]):
            time[iTime] = time[iTime].total_seconds()
        assert np.array_equal(time64, time)

    '''
        test whether power is correctly extracted from courses netCDF
    '''

    def test_get_fuel_from_netCDF(self):
        lat = np.array([1.1, 2.2, 3.3, 4.4])
        it = np.array([1, 2])
        power = np.array([[1, 4], [3.4, 5.3], [2.1, 6], [1., 5.1]])
        rpm = np.array([[10, 14], [11, 15], [20, 60], [15, 5]])
        fcr = np.array([[2, 3], [4, 5], [6, 7], [8, 9]])
        rcalm = np.array([[2.2, 2.3], [2.4, 2.5], [2.6, 2.7], [2.8, 2.9]])
        rwind = np.array([[3.2, 3.3], [3.4, 3.5], [3.6, 3.7], [3.8, 3.9]])
        rshallow = np.array([[4.2, 4.3], [4.4, 4.5], [4.6, 4.7], [4.8, 4.9]])
        rwaves = np.array([[5.2, 5.3], [5.4, 5.5], [5.6, 5.7], [5.8, 5.9]])
        rroughness = np.array([[6.2, 6.3], [6.4, 6.5], [6.6, 6.7], [6.8, 6.9]])
        wave_height = np.array([[4.1, 4.2], [4.11, 4.12], [4.21, 4.22], [4.31, 4.32]])
        wave_direction = np.array([[4.4, 4.5], [4.41, 4.42], [4.51, 4.52], [4.61, 4.62]])
        wave_period = np.array([[4.7, 4.8], [4.71, 4.72], [4.81, 4.82], [4.91, 4.92]])
        u_currents = np.array([[5.1, 5.2], [5.11, 5.12], [5.21, 5.22], [5.31, 5.32]])
        v_currents = np.array([[5.4, 5.5], [5.41, 5.42], [5.51, 5.52], [5.61, 5.62]])
        u_wind_speed = np.array([[7.1, 7.2], [7.11, 7.12], [7.21, 7.22], [7.31, 7.32]])
        v_wind_speed = np.array([[7.4, 7.5], [7.41, 7.42], [7.51, 7.52], [7.61, 7.62]])
        pressure = np.array([[5.7, 5.8], [5.71, 5.72], [5.81, 5.82], [5.91, 5.92]])
        air_temperature = np.array([[6.1, 6.2], [6.11, 6.12], [6.21, 6.22], [6.31, 6.32]])
        salinity = np.array([[6.4, 6.5], [6.41, 6.42], [6.51, 6.52], [6.61, 6.62]])
        water_temperature = np.array([[6.7, 6.8], [6.71, 6.72], [6.81, 6.82], [6.91, 6.92]])
        status = np.array([[1, 2], [2, 3], [3, 2], [1, 3]])
        message = np.array([['OK', 'OK'], ['OK', 'ERROR'],
                            ['ERROR', 'OK'], ['ERROR', 'ERROR']])

        data_vars = {'Power_brake': (["lat", "it"], power),
                     'RotationRate': (["lat", "it"], rpm),
                     'Fuel_consumption_rate': (["lat", "it"], fcr),
                     'Calm_resistance': (["lat", "it"], rcalm),
                     'Wind_resistance': (["lat", "it"], rwind),
                     'Wave_resistance': (["lat", "it"], rwaves),
                     'Shallow_water_resistance': (["lat", "it"], rshallow),
                     'Hull_roughness_resistance': (["lat", "it"], rroughness),
                     'VHM0': (["lat", "it"], wave_height),
                     'VMDR': (["lat", "it"], wave_direction),
                     'VTPK': (["lat", "it"], wave_period),
                     'utotal': (["lat", "it"], u_currents),
                     'vtotal': (["lat", "it"], v_currents),
                     'u-component_of_wind_height_above_ground': (["lat", "it"], u_wind_speed),
                     'v-component_of_wind_height_above_ground': (["lat", "it"], v_wind_speed),
                     'Pressure_reduced_to_MSL_msl': (["lat", "it"], pressure),
                     'Temperature_surface': (["lat", "it"], air_temperature),
                     'so': (["lat", "it"], salinity),
                     'thetao': (["lat", "it"], water_temperature),
                     'Status': (["lat", "it"], status),
                     'Message': (["lat", "it"], message)}

        coords = dict(lat=(["lat"], lat), it=(["it"], it), )
        attrs = dict(description="Necessary descriptions added here.")

        ds = xr.Dataset(data_vars, coords, attrs)
        print(ds)

        pol = basic_test_func.create_dummy_Tanker_object()
        ship_params = pol.extract_params_from_netCDF(ds)
        power_test = ship_params.get_power()
        rpm_test = ship_params.get_rpm()
        fuel_test = ship_params.get_fuel_rate()
        rcalm_test = ship_params.get_rcalm()
        rwind_test = ship_params.get_rwind()
        rshallow_test = ship_params.get_rshallow()
        rwaves_test = ship_params.get_rwaves()
        rroughness_test = ship_params.get_rroughness()
        wave_height_test = ship_params.get_wave_height()
        wave_direction_test = ship_params.get_wave_direction()
        wave_period_test = ship_params.get_wave_period()
        u_currents_test = ship_params.get_u_currents()
        v_currents_test = ship_params.get_v_currents()
        u_wind_speed_test = ship_params.get_u_wind_speed()
        v_wind_speed_test = ship_params.get_v_wind_speed()
        pressure_test = ship_params.get_pressure()
        air_temperature_test = ship_params.get_air_temperature()
        salinity_test = ship_params.get_salinity()
        water_temperature_test = ship_params.get_water_temperature()
        status_test = ship_params.get_status()
        message_test = ship_params.get_message()

        power_ref = np.array([1, 4, 3.4, 5.3, 2.1, 6, 1., 5.1]) * u.Watt
        rpm_ref = np.array([10, 14, 11, 15, 20, 60, 15, 5]) * 1 / u.minute
        fuel_ref = np.array([2, 3, 4, 5, 6, 7, 8, 9]) * u.kg / u.second
        rcalm_ref = np.array([2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9]) * u.newton
        rwind_ref = np.array([3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9]) * u.newton
        rshallow_ref = np.array([4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9]) * u.newton
        rwaves_ref = np.array([5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9]) * u.newton
        rroughness_ref = np.array([6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9]) * u.newton
        wave_height_ref = -99
        wave_direction_ref = -99
        wave_period_ref = -99
        u_currents_ref = -99
        v_currents_ref = -99
        u_wind_speed_ref = -99
        v_wind_speed_ref = -99
        pressure_ref = -99
        air_temperature_ref = -99
        salinity_ref = -99
        water_temperature_ref = -99
        status_ref = np.array([1, 2, 2, 3, 3, 2, 1, 3])
        message_ref = np.array(['OK', 'OK', 'OK', 'ERROR', 'ERROR', 'OK', 'ERROR', 'ERROR'])

        fuel_test = fuel_test.value * 3.6
        fuel_ref = fuel_ref.value

        assert np.array_equal(power_test, power_ref)
        assert np.array_equal(rpm_test, rpm_ref)
        assert np.allclose(fuel_ref, fuel_test, 0.00001)
        assert np.array_equal(rcalm_test, rcalm_ref)
        assert np.array_equal(rwind_test, rwind_ref)
        assert np.array_equal(rshallow_test, rshallow_ref)
        assert np.array_equal(rwaves_test, rwaves_ref)
        assert np.array_equal(rroughness_test, rroughness_ref)
        assert np.array_equal(wave_height_test, wave_height_ref)
        assert np.array_equal(wave_direction_test, wave_direction_ref)
        assert np.array_equal(wave_period_test, wave_period_ref)
        assert np.array_equal(u_currents_test, u_currents_ref)
        assert np.array_equal(v_currents_test, v_currents_ref)
        assert np.array_equal(u_wind_speed_test, u_wind_speed_ref)
        assert np.array_equal(v_wind_speed_test, v_wind_speed_ref)
        assert np.array_equal(pressure_test, pressure_ref)
        assert np.array_equal(air_temperature_test, air_temperature_ref)
        assert np.array_equal(salinity_test, salinity_ref)
        assert np.array_equal(water_temperature_test, water_temperature_ref)
        assert np.array_equal(status_test, status_ref)
        assert np.array_equal(message_test, message_ref)
        ds.close()

    '''
        check return values by maripower: has there been renaming? Do the return values have a sensible order
        of magnitude?
    '''

    def test_power_consumption_returned(self):
        # dummy weather file
        time_single = datetime.strptime('2023-07-20', '%Y-%m-%d')

        # courses test file
        courses_test = np.array([0, 180, 0, 180, 180, 0]) * u.degree
        lat_test = np.array([54.3, 54.3, 54.6, 54.6, 54.9, 54.9])
        lon_test = np.array([13.3, 13.3, 13.6, 13.6, 13.9, 13.9])

        # dummy course netCDF
        pol = basic_test_func.create_dummy_Tanker_object()
        pol.use_depth_data = False
        pol.set_boat_speed(np.array([8]) * u.meter / u.second)

        time_test = np.array([time_single, time_single, time_single, time_single, time_single, time_single])
        pol.write_netCDF_courses(courses_test, lat_test, lon_test, time_test)
        ds = pol.get_fuel_netCDF()

        power = ds['Power_brake'].to_numpy() * u.Watt
        rpm = ds['RotationRate'].to_numpy() * u.Hz
        fuel = ds['Fuel_consumption_rate'].to_numpy() * u.kg / u.s

        assert np.all(power < 10000000 * u.Watt)
        assert np.all(rpm < 100 * u.Hz)

        assert np.all(fuel < 1.5 * u.kg / u.s)
        assert np.all(power > 1000000 * u.Watt)
        assert np.all(rpm > 70 * u.Hz)
        assert np.all(fuel > 0.5 * u.kg / u.s)

    '''
        test whether lat, lon, time and courses are correctly written to course netCDF (elements and shape read from
        netCDF match properties of original array)
    '''

    def test_get_netCDF_courses_isobased(self):
        lat = np.array([1., 1., 1, 2, 2, 2])
        lon = np.array([4., 4., 4, 3, 3, 3])
        courses = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]) * u.degree
        # speed = np.array([0.01, 0.02, 0.03, 0.04, 0.05, 0.06])

        pol = basic_test_func.create_dummy_Tanker_object()
        time = np.array([datetime(2022, 12, 19), datetime(2022, 12, 19), datetime(2022, 12, 19),
                         datetime(2022, 12, 19) + timedelta(days=360),
                         datetime(2022, 12, 19) + timedelta(days=360),
                         datetime(2022, 12, 19) + timedelta(days=360)])

        pol.write_netCDF_courses(courses, lat, lon, time, None, True)
        ds = xr.open_dataset(pol.courses_path)

        lat_read = ds['lat'].to_numpy()
        lon_read = ds['lon'].to_numpy()
        courses_read = ds['courses'].to_numpy()
        time_read = ds['time'].to_numpy()

        lat_ind = np.unique(lat, return_index=True)[1]
        lon_ind = np.unique(lon, return_index=True)[1]
        time_ind = np.unique(time, return_index=True)[1]
        lat = [lat[index] for index in sorted(lat_ind)]
        lon = [lon[index] for index in sorted(lon_ind)]
        time = [time[index] for index in sorted(time_ind)]
        time = np.array(time)

        assert np.array_equal(lat, lat_read)
        assert np.array_equal(lon, lon_read)
        self.compare_times(time_read, time)

        assert courses.shape[0] == courses_read.shape[0] * courses_read.shape[1]
        for ilat in range(0, courses_read.shape[0]):
            for iit in range(0, courses_read.shape[1]):
                iprev = ilat * courses_read.shape[1] + iit
                assert courses[iprev] == np.rad2deg(courses_read[ilat][iit]) * u.degree

        ds.close()

    '''
        test whether lat, lon, time and courses are correctly written to course netCDF (elements and shape read from
        netCDF match properties of original array) for the genetic algorithm
    '''

    def test_get_netCDF_courses_GA(self):
        lat_short = np.array([1, 2, 1])
        lon_short = np.array([4, 4, 1.5])
        courses = np.array([0.1, 0.2, 0.3]) * u.degree

        pol = basic_test_func.create_dummy_Tanker_object()
        time = np.array([datetime(2022, 12, 19), datetime(2022, 12, 19) + timedelta(days=180),
                         datetime(2022, 12, 19) + timedelta(days=360)])

        pol.write_netCDF_courses(courses, lat_short, lon_short, time)
        ds = xr.open_dataset(pol.courses_path)

        lat_read = ds['lat'].to_numpy()
        lon_read = ds['lon'].to_numpy()
        courses_read = ds['courses'].to_numpy()
        time_read = ds['time'].to_numpy()

        assert np.array_equal(lat_short, lat_read)
        assert np.array_equal(lon_short, lon_read)
        self.compare_times(time_read, time)

        assert courses.shape[0] == courses_read.shape[0] * courses_read.shape[1]
        for ilat in range(0, courses_read.shape[0]):
            for iit in range(0, courses_read.shape[1]):
                iprev = ilat * courses_read.shape[1] + iit
                assert np.radians(courses[iprev]) == courses_read[ilat][iit] * u.radian

        ds.close()

    '''
        test whether lat, lon, time and courses are correctly written to course netCDF & wheather start_times_per_step
        and dist_per_step
        are correctly calculated
    '''

    def test_get_fuel_for_fixed_waypoints(self):
        bs = 6 * u.meter / u.second
        start_time = datetime.strptime("2023-07-20T10:00Z", '%Y-%m-%dT%H:%MZ')
        route_lats = np.array([54.9, 54.7, 54.5, 54.2])
        route_lons = np.array([13.2, 13.4, 13.7, 13.9])

        pol = basic_test_func.create_dummy_Tanker_object()
        pol.use_depth_data = False
        pol.set_boat_speed(bs)

        waypoint_dict = RouteParams.get_per_waypoint_coords(route_lons, route_lats, start_time, bs)

        ship_params = pol.get_ship_parameters(waypoint_dict['courses'], waypoint_dict['start_lats'],
                                              waypoint_dict['start_lons'], waypoint_dict['start_times'], None)
        ship_params.print()

        ds = xr.open_dataset(pol.courses_path)
        test_lat_start = ds.lat
        test_lon_start = ds.lon
        test_courses = np.rad2deg(ds.courses.to_numpy()[:, 0])
        test_time = ds.time.to_numpy()

        test_time_dt = np.full(3, datetime(1970, 1, 1, 0, 0))
        for t in range(0, 3):
            test_time_dt[t] = utils.convert_npdt64_to_datetime(test_time[t])

        ref_lat_start = np.array([54.9, 54.7, 54.5])
        ref_lon_start = np.array([13.2, 13.4, 13.7])
        ref_courses = np.array([149.958, 138.89, 158.685])
        ref_dist = np.array([25712., 29522., 35836.]) * u.meter
        ref_time = np.array([start_time, start_time + timedelta(seconds=ref_dist[0].value / bs.value),
                             start_time + timedelta(seconds=ref_dist[0].value / bs.value) + timedelta(
                                 seconds=ref_dist[1].value / bs.value)])

        assert test_lon_start.any() == ref_lon_start.any()
        assert test_lat_start.any() == ref_lat_start.any()
        assert np.allclose(test_courses, ref_courses, 0.1)
        assert utils.compare_times(test_time_dt, ref_time) is True
        assert np.allclose(waypoint_dict['dist'], ref_dist, 0.1)

    '''
        test whether power and wind resistance that are returned by maripower lie on an ellipse. Wind is coming from the
        east, ellipse generated needs to be shifted towards the left
    '''

    def test_wind_force(self):
        lats = np.full(10, 54.9)  # 37
        lons = np.full(10, 13.2)
        courses = np.linspace(0, 360, 10) * u.degree
        courses_rad = utils.degree_to_pmpi(courses)

        time = np.full(10, datetime.strptime("2023-07-20T10:00Z", '%Y-%m-%dT%H:%MZ'))
        bs = 6

        pol = basic_test_func.create_dummy_Tanker_object()
        pol.use_depth_data = False
        pol.set_boat_speed(bs)

        ship_params = pol.get_ship_parameters(courses, lats, lons, time, None, True)
        power = ship_params.get_power()
        rwind = ship_params.get_rwind()

        fig, axes = plt.subplots(1, 2, subplot_kw={'projection': 'polar'})

        axes[0].plot(courses_rad, power)
        axes[0].legend()
        for ax in axes.flatten():
            ax.set_rlabel_position(-22.5)  # Move radial labels away from plotted line
            ax.set_theta_zero_location("S")
            ax.grid(True)
        axes[1].plot(courses_rad, rwind)
        axes[0].set_title("Power", va='bottom')
        axes[1].set_title("Wind resistence", va='top')

        plt.show()

    def test_maripower_via_dict_config(self):
        dirname = os.path.dirname(__file__)

        weather_path = os.path.join(dirname, 'data/reduced_testdata_weather.nc')
        courses_path = os.path.join(dirname, 'data/CoursesRoute.nc')
        depth_path = os.path.join(dirname, 'data/reduced_testdata_depth.nc')

        speed = 6 * u.meter / u.second
        drought_aft = 10 * u.meter
        drought_fore = 10 * u.meter
        roughness_distr = 5
        roughness_lev = 5

        config = {
            "COURSES_FILE": courses_path,
            "DEPTH_DATA": depth_path,
            "WEATHER_DATA": weather_path,
            'BOAT_FUEL_RATE': 167,
            'BOAT_HBR': 30,
            'BOAT_LENGTH': 180,
            'BOAT_SMCR_POWER': 6502,
            'BOAT_SMCR_SPEED': 6,
            'BOAT_SPEED': 6,
            "BOAT_DRAUGHT_AFT": 10,
            "BOAT_DRAUGHT_FORE": 10,
            'BOAT_ROUGHNESS_DISTRIBUTION_LEVEL': 5,
            'BOAT_ROUGHNESS_LEVEL': 5.,
            'BOAT_BREADTH': 32
        }

        pol = MariPowerTanker(init_mode="from_dict", config_dict=config)

        assert pol.speed == speed
        assert pol.depth_path == depth_path
        assert pol.weather_path == weather_path
        assert pol.courses_path == courses_path
        assert (pol.hydro_model.Draught_AP == [drought_aft.value]).all()
        assert (pol.hydro_model.Draught_FP == [drought_fore.value]).all()
        assert pol.hydro_model.Roughness_Distribution_Level == roughness_distr
        assert pol.hydro_model.Roughness_Level == roughness_lev
        assert pol.use_depth_data
