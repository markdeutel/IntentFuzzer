from drozer.modules import common

class FuzzerPackageManager(common.PackageManager.PackageManagerProxy, common.Filters):

    def get_receivers(self, packageNameString):
        receivers = self.packageManager().getPackageInfo(packageNameString, self.packageManager().GET_RECEIVERS).receivers
        if str(receivers) == "null":
            return []
        else:
            receivers = self.match_filter(receivers, "exported", True)
            return receivers                   
        
    def get_activities(self, packageNameString):
        activities = self.packageManager().getPackageInfo(packageNameString, self.packageManager().GET_ACTIVITIES).activities
        if str(activities) == "null":
            return []
        else:
            activities = self.match_filter(activities, "exported", True)
            return activities
        
    def get_services(self, packageNameString):
        services = self.packageManager().getPackageInfo(packageNameString, self.packageManager().GET_SERVICES).services
        if str(services) == "null":
            return []
        else:
            services = self.match_filter(services, "exported", True)
            return services
