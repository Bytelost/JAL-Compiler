START{
    
    INT var1;
    FLOAT var2;
    BOOL var3;

    IF(var3){
        var1 = 1;
        var4 = -0.5;
    }

    IF(var3){
        var1 = 1;
        var4 = -0.5;
    } ELSE {
        var1 = 1;
        var4 = -0.5;
    }

    FOR(var3){
        var1 = 1;
        var4 = -0.5;
    }

    FOR(var2){
        var1 = 1;
        var4 = -0.5;
    }

    WHILE(var3){
        var1 = 1;
        var4 = -0.5;
    }

    var1 = 1;
    var4 = -0.5;
    
    var2 = DIV(var1, 2);

    OUT(var2);

    END;
}