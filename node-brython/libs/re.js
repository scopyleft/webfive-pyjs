$module = {
    __getattr__ : function(attr){
        var res = this[attr]
        if(res===undefined){throw AttributeError("module re has no attribute '"+attr+"'")}
        return res
    },
    I : 'i',
    M : 'm',
    findall : function(pattern,string,flags){
        var $ns=$MakeArgs('re.search',arguments,['pattern','string'],{},'args','kw')
        var args = $ns['args']
        if(args.length>0){var flags=args[0]}
        else{var flags = $ns['kw'].get('flags','')}
        flags += 'gm'
        var jsp = new RegExp(pattern,flags)
        var jsmatch = string.match(jsp)
        if(jsmatch===null){return []}
        return jsmatch
    },
    search : function(pattern,string){
        var $ns=$MakeArgs('re.search',arguments,['pattern','string'],{},'args','kw')
        var args = $ns['args']
        if(args.length>0){var flags=args[0]}
        else{var flags = $ns['kw'].get('flags','')}
        var jsp = new RegExp(pattern,flags)
        var jsmatch = string.match(jsp)
        if(jsmatch===null){return None}
        var mo = new Object()
        mo.groups = function(){return jsmatch.slice(1)}
        mo.start = function(){return jsmatch.index}
        return JSObject(mo)
    },
    sub : function(pattern,repl,string){
        var $ns=$MakeArgs('re.search',arguments,['pattern','repl','string'],{},'args','kw')
        for($var in $ns){eval("var "+$var+"=$ns[$var]")}
        var args = $ns['args']
        var count = $ns['kw'].get('count',0)
        var flags = $ns['kw'].get('flags','')
        if(args.length>0){var count=args[0]}
        if(args.length>1){var flags=args[1]}
        if(typeof repl==="string"){
            // backreferences are \1, \2... in Python but $1,$2... in Javascript
            repl = repl.replace(/\\(\d+)/g,'$$$1')
        }
        if(count==0){flags+='g'}
        var jsp = new RegExp(pattern,flags)
        return string.replace(jsp,repl)
    }
}

$module.__class__ = $module // defined in $py_utils
$module.__str__ = function(){return "<module 're'>"}
