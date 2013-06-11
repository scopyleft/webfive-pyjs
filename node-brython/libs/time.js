$module =  {

    __getattr__ : function(attr){return this[attr]},

    clear_interval : function(int_id){window.clearInterval(int_id)},
    
    set_interval : function(func,interval){
        return int(window.setInterval(func,interval))
    },

    set_timeout : function(func,interval){window.setTimeout(func,interval)},

    localtime : function(secs){ 
       var d=new Date();
       if (secs === undefined || secs === None) {return d.getTime()}

       // calculate if we are in daylight savings time or not.
       // borrowed from http://stackoverflow.com/questions/11887934/check-if-daylight-saving-time-is-in-effect-and-if-it-is-for-how-many-hours
       var jan = new Date(d.getFullYear(), 0, 1);
       var jul = new Date(d.getFullYear(), 6, 1);
       var dst=int(d.getTimezoneOffset() < Math.max(jan.getTimezoneOffset(), jul.getTimezoneOffset()));

       return list([d.getFullYear(), d.getMonth()+1, d.getDate(), d.getHours(),
                    d.getMinutes(), d.getSeconds(), d.getDay(), 0, dst])
       //fixme  (second to last value is 0 which is the number of days in this year..)
    },
    time : function(){return (new Date()).getTime()},
    
    strftime : function(format,arg){

        function ns(arg,nb){
            // left padding with 0
            var res = arg.toString()
            while(res.length<nb){res = '0'+res}
            return res
        }
        if(arg){var obj = new Date(arg)}else{var obj=new Date()}
        var res = format
        res = res.replace(/%H/,ns(obj.getHours(),2))
        res = res.replace(/%M/,ns(obj.getMinutes(),2))
        res = res.replace(/%S/,ns(obj.getSeconds(),2))
        res = res.replace(/%Y/,ns(obj.getFullYear(),4))
        res = res.replace(/%y/,ns(obj.getFullYear(),4).substr(2))
        res = res.replace(/%m/,ns(obj.getMonth()+1,2))
        res = res.replace(/%d/,ns(obj.getDate(),2))
        return res
    }
}
