$module = {
    __getattr__ : function(attr){return this[attr]},
    random:function(){return float(Math.random())},
    randint:function(a,b){return int(Math.floor(Math.random()*(b-a)+a))}
}
$module.__class__ = $module // defined in $py_utils
$module.__str__ = function(){return "<module 'random'>"}
