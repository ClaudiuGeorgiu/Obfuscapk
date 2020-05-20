.class public Lcom/obfuscapk/demo/OrderDemo;
.super Ljava/lang/Object;
.source "OrderDemo.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .prologue
    .line 6
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static getGotoMessage()Ljava/lang/String;
    .locals 5

    const v0, 7
    const v1, 4
    add-int v0, v0, v1
    rem-int v0, v0, v1
    if-gtz v0, :EbAukdQwmmPELTjd
    goto/32 :bPdknjDcQesDQUPu
    :EbAukdQwmmPELTjd
    :KbkerIsqVXNivOzU

    .prologue
    .line 9
    new-instance v3, Ljava/util/ArrayList;

    invoke-direct {v3}, Ljava/util/ArrayList;-><init>()V

    .line 11
    .local v3, "messages":Ljava/util/ArrayList;, "Ljava/util/ArrayList<Ljava/lang/String;>;"
    const-string/jumbo v0, "message1"

    .line 12
    .local v0, "message1":Ljava/lang/String;
    invoke-virtual {v3, v0}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 14
    const-string/jumbo v1, "message2"

    .line 15
    .local v1, "message2":Ljava/lang/String;
    invoke-virtual {v3, v1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 17
    const-string/jumbo v2, "message3"

    .line 18
    .local v2, "message3":Ljava/lang/String;
    invoke-virtual {v3, v2}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 20
    invoke-virtual {v3}, Ljava/util/ArrayList;->toArray()[Ljava/lang/Object;

    move-result-object v4

    invoke-static {v4}, Ljava/util/Arrays;->toString([Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v4

    return-object v4
    :bPdknjDcQesDQUPu
    goto/32 :KbkerIsqVXNivOzU
.end method
