.class public Lcom/obfuscapk/demo/OrderDemo;
.super Ljava/lang/Object;
.source "OrderDemo.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .prologue
    .line 6
    goto/32 :l_tQCKFqpiHRBRQciF_0

    nop

    :l_oshIgQxSuXqmHWGJ_1
    return-void
    :l_tQCKFqpiHRBRQciF_0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    goto/32 :l_oshIgQxSuXqmHWGJ_1

    nop

.end method

.method public static getGotoMessage()Ljava/lang/String;
    .locals 5

    .prologue
    .line 9
    goto/32 :l_eBkbmfkmuZTYwAgJ_0

    nop

    :l_QMdQTrZBOlokaNUc_10
    return-object v4
    :l_kOqAKmRqIzEtMrpu_2
    const-string/jumbo v0, "message1"

    .line 12
    .local v0, "message1":Ljava/lang/String;
    goto/32 :l_xReCXfmtkdGhgSBm_3

    nop

    :l_sDhILXmJzXsfcXUr_8
    invoke-virtual {v3}, Ljava/util/ArrayList;->toArray()[Ljava/lang/Object;

    move-result-object v4

    goto/32 :l_hxqpYFdVKuYdybMT_9

    nop

    :l_CvcmNMlasjdVLEnV_5
    invoke-virtual {v3, v1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 17
    goto/32 :l_dbUktrjcDOLMeNVZ_6

    nop

    :l_KvFcAHhVAtjRMgfv_1
    invoke-direct {v3}, Ljava/util/ArrayList;-><init>()V

    .line 11
    .local v3, "messages":Ljava/util/ArrayList;, "Ljava/util/ArrayList<Ljava/lang/String;>;"
    goto/32 :l_kOqAKmRqIzEtMrpu_2

    nop

    :l_xReCXfmtkdGhgSBm_3
    invoke-virtual {v3, v0}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 14
    goto/32 :l_ILLEMEdMoEmHnmxs_4

    nop

    :l_eBkbmfkmuZTYwAgJ_0
    new-instance v3, Ljava/util/ArrayList;

    goto/32 :l_KvFcAHhVAtjRMgfv_1

    nop

    :l_dbUktrjcDOLMeNVZ_6
    const-string/jumbo v2, "message3"

    .line 18
    .local v2, "message3":Ljava/lang/String;
    goto/32 :l_CVAqRcEaIIREDEwX_7

    nop

    :l_hxqpYFdVKuYdybMT_9
    invoke-static {v4}, Ljava/util/Arrays;->toString([Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v4

    goto/32 :l_QMdQTrZBOlokaNUc_10

    nop

    :l_ILLEMEdMoEmHnmxs_4
    const-string/jumbo v1, "message2"

    .line 15
    .local v1, "message2":Ljava/lang/String;
    goto/32 :l_CvcmNMlasjdVLEnV_5

    nop

    :l_CVAqRcEaIIREDEwX_7
    invoke-virtual {v3, v2}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z

    .line 20
    goto/32 :l_sDhILXmJzXsfcXUr_8

    nop

.end method
