.class public Lcom/obfuscapk/demo/OrderDemo;
.super Ljava/lang/Object;
.source "OrderDemo.java"


# direct methods
.method public static CaxLmSVQaEISXHgM(Ljava/util/ArrayList;Ljava/lang/Object;)Z
    .locals 1

    invoke-virtual {p0, p1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    move-result v0

    return v0
.end method

.method public static RFtgxYkkHgZTZAyR(Ljava/util/ArrayList;Ljava/lang/Object;)Z
    .locals 1

    invoke-virtual {p0, p1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    move-result v0

    return v0
.end method

.method public static uwzJipmHrJxSPOuT(Ljava/util/ArrayList;Ljava/lang/Object;)Z
    .locals 1

    invoke-virtual {p0, p1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    move-result v0

    return v0
.end method

.method public static SOrHOqcDYYLsEuaK(Ljava/util/ArrayList;)[Ljava/lang/Object;
    .locals 1

    invoke-virtual {p0}, Ljava/util/ArrayList;->toArray()[Ljava/lang/Object;

    move-result-object v0

    return-object v0
.end method

.method public static QnaFXsjaPRCCYNho([Ljava/lang/Object;)Ljava/lang/String;
    .locals 1

    invoke-static {p0}, Ljava/util/Arrays;->toString([Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method public constructor <init>()V
    .locals 0

    .prologue
    .line 6
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static getGotoMessage()Ljava/lang/String;
    .locals 5

    .prologue
    .line 9
    new-instance v3, Ljava/util/ArrayList;

    invoke-direct {v3}, Ljava/util/ArrayList;-><init>()V

    .line 11
    .local v3, "messages":Ljava/util/ArrayList;, "Ljava/util/ArrayList<Ljava/lang/String;>;"
    const-string/jumbo v0, "message1"

    .line 12
    .local v0, "message1":Ljava/lang/String;
    invoke-static {v3, v0}, Lcom/obfuscapk/demo/OrderDemo;->CaxLmSVQaEISXHgM(Ljava/util/ArrayList;Ljava/lang/Object;)Z

    .line 14
    const-string/jumbo v1, "message2"

    .line 15
    .local v1, "message2":Ljava/lang/String;
    invoke-static {v3, v1}, Lcom/obfuscapk/demo/OrderDemo;->RFtgxYkkHgZTZAyR(Ljava/util/ArrayList;Ljava/lang/Object;)Z

    .line 17
    const-string/jumbo v2, "message3"

    .line 18
    .local v2, "message3":Ljava/lang/String;
    invoke-static {v3, v2}, Lcom/obfuscapk/demo/OrderDemo;->uwzJipmHrJxSPOuT(Ljava/util/ArrayList;Ljava/lang/Object;)Z

    .line 20
    invoke-static {v3}, Lcom/obfuscapk/demo/OrderDemo;->SOrHOqcDYYLsEuaK(Ljava/util/ArrayList;)[Ljava/lang/Object;

    move-result-object v4

    invoke-static {v4}, Lcom/obfuscapk/demo/OrderDemo;->QnaFXsjaPRCCYNho([Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v4

    return-object v4
.end method
