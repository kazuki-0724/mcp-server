import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Zipcloud APIのレスポンス型定義
interface ZipcloudResponse {
  message: string | null;
  results: Array<{
    address1: string;
    address2: string;
    address3: string;
    kana1: string;
    kana2: string;
    kana3: string;
    prefcode: string;
    zipcode: string;
  }> | null;
  status: number;
}

const server = new Server(
  {
    name: "zipcode-api-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_address_by_zipcode",
        description: "日本の郵便番号から住所を取得します",
        inputSchema: {
          type: "object",
          properties: {
            zipcode: {
              type: "string",
              description: "7桁の郵便番号（例: 1000001、ハイフンなし）",
            },
          },
          required: ["zipcode"],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "get_address_by_zipcode") {
    // argumentsの型を安全にキャスト
    const args = request.params.arguments as { zipcode?: string };
    const zipcode = args.zipcode;

    if (!zipcode) {
      throw new Error("zipcodeは必須パラメータです");
    }

    const url = `https://zipcloud.ibsnet.co.jp/api/search?zipcode=${zipcode}`;

    try {
      const response = await fetch(url);
      const data = (await response.json()) as ZipcloudResponse;

      if (data.results && data.results.length > 0) {
        const addr = data.results[0];
        const fullAddress = `${addr.address1}${addr.address2}${addr.address3}`;
        
        return {
          content: [
            {
              type: "text",
              text: `郵便番号 ${zipcode} の住所は「${fullAddress}」です。`,
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `郵便番号 ${zipcode} に該当する住所が見つかりませんでした。`,
            },
          ],
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      return {
        content: [
          {
            type: "text",
            text: `APIの呼び出し中にエラーが発生しました: ${errorMessage}`,
          },
        ],
        isError: true,
      };
    }
  }

  throw new Error("Tool not found");
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Zipcode MCP Server (TypeScript) is running on stdio");
}

main().catch(console.error);