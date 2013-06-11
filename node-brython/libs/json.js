$module =  {

    __getattr__ : function(attr){return this[attr]},

    parse : function(json_obj){
        var res = JSON.parse(json_obj)
        var _class = res['class']
        if(_class===undefined){return $JS2Py(res)}
        else if(['int','str','list'].indexOf(_class)>-1){return res.obj}
        else if(_class==='float'){return res.obj.value}
        else if(_class==='dict'){
            var res1 = dict()
            for(var i=0;i<res.obj.$keys.length;i++){
                res1.__setitem__(res.obj.$keys[i],res.obj.$values[i])
            }
            return res1
        }else if(_class==='set'){
            var res1 = set()
            for(var i=0;i<res.obj.items.length;i++){
                res1.add(res.obj.items[i])
            }
            return res1
        }else{throw ValueError("can't parse JSON object "+json_obj)}
    },

    stringify : function(obj){
        return JSON.stringify({'class':obj.__class__.__name__,'obj':obj})
    },
}