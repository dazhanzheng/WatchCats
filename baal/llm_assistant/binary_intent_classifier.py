"""
二进制意图分类器

使用极简的二进制输出格式，每个位代表一个工具的使用状态
输出格式：3位二进制字符串
- 第1位：是否是普通聊天 (1=聊天, 0=需要工具)
- 第2位：是否需要统计查询 (1=需要, 0=不需要)
- 第3位：是否需要日程查询 (1=需要, 0=不需要)

示例：
- "100" = 普通聊天
- "010" = 只需要统计
- "001" = 只需要日程
- "011" = 需要统计和日程
"""

from typing import Tuple
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class BinaryIntentClassifier:
    """二进制意图分类器"""
    
    def __init__(self, llm: ChatOpenAI):
        """
        初始化分类器
        
        Args:
            llm: LangChain LLM 实例
        """
        self.llm = llm
        
        # 构建提示词
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个意图分类器。分析用户输入，输出3位二进制数字。

输出格式（必须严格遵守）：
- 只输出3个数字，每个数字只能是0或1
- 第1位：普通聊天=1，需要工具=0
- 第2位：需要统计=1，不需要=0
- 第3位：需要日程=1，不需要=0

示例：
用户："你好" → 输出：100
用户："我今天做了什么" → 输出：010
用户："明天有什么安排" → 输出：001
用户："今天工作了多久？明天有会议吗" → 输出：011

重要：只输出3个数字，不要有任何其他内容！"""),
            ("human", "{input}")
        ])
        
        # 构建链
        self.chain = self.prompt | self.llm
    
    def classify(self, user_input: str) -> str:
        """
        分类用户输入
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            str: 3位二进制字符串
        """
        response = self.chain.invoke({"input": user_input})
        
        # 提取内容
        if hasattr(response, 'content'):
            result = response.content.strip()
        else:
            result = str(response).strip()
        
        # 验证格式（只保留前3个0/1字符）
        binary_str = ""
        for char in result:
            if char in "01" and len(binary_str) < 3:
                binary_str += char
        
        # 如果不足3位，补0
        while len(binary_str) < 3:
            binary_str += "0"
        
        return binary_str[:3]
    
    @staticmethod
    def parse_binary(binary_str: str) -> Tuple[bool, bool, bool]:
        """
        解析二进制字符串
        
        Args:
            binary_str: 3位二进制字符串
            
        Returns:
            Tuple[bool, bool, bool]: (is_chat, needs_stats, needs_schedule)
        """
        if len(binary_str) != 3:
            # 默认为普通聊天
            return (True, False, False)
        
        is_chat = binary_str[0] == '1'
        needs_stats = binary_str[1] == '1'
        needs_schedule = binary_str[2] == '1'
        
        # 逻辑检查：如果需要工具，则不是普通聊天
        if needs_stats or needs_schedule:
            is_chat = False
        
        return (is_chat, needs_stats, needs_schedule) 