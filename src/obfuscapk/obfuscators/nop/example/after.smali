.class public Lcom/obfuscapk/demo/NopDemo;
.super Ljava/lang/Object;
.source "NopDemo.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .prologue
    .line 3
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
    nop
.end method

.method public static getNopMessage(Ljava/lang/String;)Ljava/lang/String;
    .locals 5
    .param p0, "from"    # Ljava/lang/String;

    .prologue
    .line 6
    const-string/jumbo v2, "Nop message: "
    nop

    .line 7
    .local v2, "messageStart":Ljava/lang/String;
    const-string/jumbo v1, "sending a nop message from "
    nop
    nop
    nop
    nop
    nop

    .line 8
    .local v1, "messageBody":Ljava/lang/String;
    new-instance v3, Ljava/lang/StringBuilder;
    nop
    nop
    nop
    nop
    nop

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3
    nop
    nop
    nop
    nop

    invoke-virtual {v3, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3
    nop
    nop
    nop

    invoke-virtual {v3, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3
    nop
    nop
    nop
    nop

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0
    nop
    nop

    .line 9
    .local v0, "finalMessage":Ljava/lang/String;
    new-instance v3, Ljava/lang/StringBuilder;
    nop
    nop
    nop

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3
    nop
    nop
    nop
    nop

    const-string/jumbo v4, "!"
    nop
    nop
    nop
    nop

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3
    nop
    nop
    nop

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0
    nop
    nop
    nop
    nop

    .line 10
    return-object v0
    nop
    nop
    nop
    nop
    nop
.end method
