"""
class to run WRF
Authors: Wang Fei
History: 2018.03.23
"""
from namelist import NameList as Nl
import datetime
import os

# configurations
WPS_DIR = r"/home/wangf/WPS/"
WRF_ROOT = r"/home/wangf/WRFV3/"
WRF_RUN_DIR = os.path.join(WRF_ROOT, r"test/em_real")


class RunCase:
    """
    """

    def __init__(self, max_dom=2,
                 start_date=None,
                 day_shift=None, hour=0,
                 forecast_length=2):

        self.max_dom = max_dom
        self.wps_namelist = Nl()
        self.wrf_namelist = Nl()

        # set forecast range for real.exe
        self.day_shift = day_shift
        self.forecast_length = forecast_length

        if self.day_shift is not None:
            now_date = datetime.datetime.now()

            st_date = now_date + datetime.timedelta(days=self.day_shift)
            self.st_date = datetime.datetime(year=st_date.year,
                                             month=st_date.month,
                                             day=st_date.day,
                                             hour=hour)
        else:
            if start_date is None:
                print "start date not given!"
                exit()
            self.st_date = datetime.datetime.strptime(start_date, "%Y%m%d")

        self.ed_date = self.st_date + datetime.timedelta(days=self.forecast_length)

    def update_wps(self):
        """
        modify WPS namelist.
        """
        dt_format = "%Y-%m-%d_%H:%M:%S"

        self.wps_namelist.load("template_namelist.wps")
        self.wps_namelist["share"]["max_dom"] = "%s" % self.max_dom
        self.wps_namelist["share"]["start_date"] = ["'%s'" % self.st_date.strftime(dt_format), ] * self.max_dom
        self.wps_namelist["share"]["end_date"] = ["'%s'" % self.ed_date.strftime(dt_format), ] * self.max_dom

        self.wps_namelist.dump(os.path.join(WPS_DIR, "namelist.wps"))

    def update_wrf(self):
        """
        modify WRF namelist.
        """

        # modify WRF namelist
        self.wrf_namelist.load("template_namelist.input")

        # modify domain arguments in WRF namelist to match WPS namelist.
        dom_list = ["parent_id", "parent_grid_ratio", "i_parent_start", "j_parent_start",
                    "max_dom", "e_we", "e_sn", "dx", "dy", "interval_seconds"]

        # # modify grid options
        for dom_arg in dom_list:
            if dom_arg in ["max_dom", "interval_seconds"]:
                dom_value = self.wps_namelist["share"][dom_arg]
            else:
                dom_value = self.wps_namelist["geogrid"][dom_arg]

            if dom_arg in ["interval_seconds", ]:
                self.wrf_namelist["time_control"][dom_arg] = dom_value
            elif dom_arg in ["dx", "dy"]:
                self.wrf_namelist["domains"][dom_arg] = [
                    str(float(dom_value[0]) / float(self.wps_namelist["geogrid"]["parent_grid_ratio"][idom]))
                    for idom in range(self.max_dom)]
            else:
                self.wrf_namelist["domains"][dom_arg] = dom_value

        # # modify date options
        for date_char in ["year", "month", "day", "hour", "minute", "second"]:
            self.wrf_namelist["time_control"]["start_%s" % date_char] = [str(getattr(self.st_date, date_char)),
                                                                         ] * self.max_dom
            self.wrf_namelist["time_control"]["end_%s" % date_char] = [str(getattr(self.ed_date, date_char)),
                                                                       ] * self.max_dom

        self.wrf_namelist["time_control"]["run_days"] = str(self.forecast_length)
        self.wrf_namelist["time_control"]["run_hours"] = "0"

        self.wrf_namelist.dump(os.path.join(WRF_RUN_DIR, "namelist.input"))

    def run(self, run_geo=True):
        """
        main function to run the whole process.
        """
        # update WPS namelist.
        self.update_wps()

        # run WPS
        #os.system("./run_wps.sh %s %s %s" % (self.st_date.strftime("%Y%m%d%H"), WPS_DIR, run_geo))

        # update WRF namelist.
        self.update_wrf()

        # run real.exe
        os.system("./run_wrf.sh %s %s %s %s" % 
                  (WPS_DIR, WRF_RUN_DIR, self.st_date.strftime("%Y%m%d%H"), self.max_dom))


if __name__ == "__main__":
    # wrf_case = RunCase(day_shift=0)
    wrf_case = RunCase(start_date="20180329", hour=0)
    wrf_case.run(run_geo=False)

