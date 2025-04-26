import numpy as np

class BudgetTool:
    def __init__(self):
        pass

    def gaussian_budget_allocation(self, total_budget, num_users, std_dev_factor=0.1):
        """
        高斯分布预算分配算法

        参数:
        - total_budget: 总预算
        - num_users: 用户数量
        - std_dev_factor: 标准差因子（控制预算分配的离散程度，默认为0.1）

        返回:
        - 分配给每个用户的预算列表
        """
        # 计算每个用户的平均预算
        mean_budget = total_budget / num_users
        
        # 计算标准差（这里我们用均值的一定比例作为标准差）
        std_dev = mean_budget * std_dev_factor
        
        # 生成符合高斯分布的预算分配，并直接取整
        budgets = np.random.normal(mean_budget, std_dev, num_users).round().astype(int)
        
        # 调整预算分配以确保总和等于总预算
        difference = int(total_budget - budgets.sum())
        if difference != 0:
            # 找到一个随机用户来调整预算差异
            adjust_user_index = np.random.choice(np.where(budgets > 0)[0])
            budgets[adjust_user_index] += difference
        
        # 统计各个金额的数量分布
        budget_distribution = {}
        for budget in budgets:
            if budget in budget_distribution:
                budget_distribution[budget] += 1
            else:
                budget_distribution[budget] = 1

        # 打印日志统计信息
        print("预算分配金额的数量分布：")
        for amount, count in sorted(budget_distribution.items()):
            print(f"金额 {amount}: {count} 次")

        return budgets.tolist()

    def get_tool_schema(self):
        return {
            "type": "function",
            "function": {
                "name": "gaussian_budget_allocation",
                "description": "根据高斯分布分配预算给用户",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "total_budget": {
                            "type": "number",
                            "description": "总预算"
                        },
                        "num_users": {
                            "type": "integer",
                            "description": "用户数量"
                        },
                        "std_dev_factor": {
                            "type": "number",
                            "description": "标准差因子（控制预算分配的离散程度，默认为0.1）"
                        }
                    },
                    "required": ["total_budget", "num_users"]
                }
            }
        }

if __name__ == "__main__":
    budget_tool = BudgetTool()

    # 获取用户输入的总预算和用户数量
    try:
        total_budget = float(input("请输入总预算: "))
        num_users = int(input("请输入用户数量: "))
        if num_users <= 0:
            raise ValueError("用户数量必须大于0")
        
        allocated_budgets = budget_tool.gaussian_budget_allocation(total_budget, num_users)
        print("分配给每个用户的预算：")
        print(allocated_budgets)
        print("总预算：", sum(allocated_budgets))
    except ValueError as e:
        print(f"输入错误: {e}")
