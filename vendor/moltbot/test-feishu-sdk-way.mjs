
package com.lark.oapi.sample.apiall.imv1;
import com.google.gson.JsonParser;
import com.lark.oapi.Client;
import com.lark.oapi.core.utils.Jsons;
import com.lark.oapi.service.im.v1.model.*;
import java.util.HashMap;
import com.lark.oapi.core.request.RequestOptions;

// SDK 使用文档：https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/java-sdk-guide/preparations
// 复制该 Demo 后, 需要将 "YOUR_APP_ID", "YOUR_APP_SECRET" 替换为自己应用的 APP_ID, APP_SECRET.
// 以下示例代码默认根据文档示例值填充，如果存在代码问题，请在 API 调试台填上相关必要参数后再复制代码使用
public class CreateMessageSample {

	public static void main(String arg[]) throws Exception {
		// 构建client
		Client client = Client.newBuilder("cli_a9f05a5e0378dcb0", "KdosR8d6vhlLdM6yP9nrUdSwb2VoevJr").build();

		// 创建请求对象
		CreateMessageReq req = CreateMessageReq.newBuilder()
			.receiveIdType("chat_id")
			.createMessageReqBody(CreateMessageReqBody.newBuilder()
				.receiveId("oc_d130fd4a7085e4cf5f313f27d3e180bd")
				.msgType("text")
				.content("{\"text\":\"test content\"}")
				.uuid("选填，每次调用前请更换，如a0d69e20-1dd1-458b-k525-dfeca4015204")
				.build())
			.build();

		// 发起请求
		CreateMessageResp resp = client.im().v1().message().create(req);

		// 处理服务端错误
		if(!resp.success()) {
			System.out.println(String.format("code:%s,msg:%s,reqId:%s, resp:%s",
				resp.getCode(), resp.getMsg(), resp.getRequestId(), Jsons.createGSON(true, false).toJson(JsonParser.parseString(new String(resp.getRawResponse().getBody(), StandardCharsets.UTF_8)))));
			return;
		}

		// 业务数据处理
		System.out.println(Jsons.DEFAULT.toJson(resp.getData()));
	}
}
