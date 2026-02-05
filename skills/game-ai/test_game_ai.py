#!/usr/bin/env python3
"""
测试游戏AI系统
"""

# 直接导入game-ai-engine.py中的所有类和函数
with open('game-ai-engine.py', 'r') as f:
    code = f.read()

# 移除main()调用部分以避免在import时执行
if '__name__' in code:
    code = code[:code.index('if __name__')]

exec(code)


def test_game_state_generation():
    """测试游戏状态生成"""
    print('测试1: 游戏状态生成...')

    # 测试MOBA游戏状态
    moba_state = GameState('moba')
    assert moba_state.game_type == 'moba', '游戏类型应该正确'
    assert 'team_gold' in moba_state.state, '应该有team_gold字段'
    assert 'team_kills' in moba_state.state, '应该有team_kills字段'
    assert len(moba_state.state['team_gold']) == 2, '应该有2支队伍'

    # 测试国际象棋游戏状态
    chess_state = GameState('chess')
    assert chess_state.game_type == 'chess', '游戏类型应该正确'
    assert 'board' in chess_state.state, '应该有board字段'
    assert 'turn' in chess_state.state, '应该有turn字段'
    assert len(chess_state.state['board']) == 8, '棋盘应该是8x8'

    # 测试FPS游戏状态
    fps_state = GameState('fps')
    assert fps_state.game_type == 'fps', '游戏类型应该正确'
    assert 'team_score' in fps_state.state, '应该有team_score字段'
    assert 'team_kills' in fps_state.state, '应该有team_kills字段'

    print('  ✓ 游戏状态生成测试通过')
    return True


def test_farming_script_creation():
    """测试资源采集脚本创建"""
    print('测试2: 资源采集脚本创建...')

    # 测试MOBA脚本
    moba_script = ScriptEngine.create_farming_script('moba')
    assert 'name' in moba_script, '脚本应该有name字段'
    assert 'steps' in moba_script, '脚本应该有steps字段'
    assert 'efficiency' in moba_script, '脚本应该有efficiency字段'
    assert 'risk_level' in moba_script, '脚本应该有risk_level字段'
    assert isinstance(moba_script['steps'], list), 'steps应该是列表'
    assert len(moba_script['steps']) > 0, 'steps不应该为空'
    assert 0 <= moba_script['efficiency'] <= 100, 'efficiency应该在0-100之间'
    assert moba_script['risk_level'] in ['low', 'medium', 'high'], 'risk_level应该是有效值'

    # 测试RPG脚本
    rpg_script = ScriptEngine.create_farming_script('rpg')
    assert rpg_script['name'] != '', '脚本name不应该为空'

    # 测试FPS脚本
    fps_script = ScriptEngine.create_farming_script('fps')
    assert fps_script['name'] != '', '脚本name不应该为空'

    print('  ✓ 资源采集脚本创建测试通过')
    return True


def test_quest_script_creation():
    """测试任务脚本创建"""
    print('测试3: 任务脚本创建...')

    # 测试每日任务脚本
    daily_script = ScriptEngine.create_quest_script('daily')
    assert 'name' in daily_script, '脚本应该有name字段'
    assert 'tasks' in daily_script, '脚本应该有tasks字段'
    assert 'estimated_time' in daily_script, '脚本应该有estimated_time字段'
    assert 'reward_value' in daily_script, '脚本应该有reward_value字段'
    assert daily_script['estimated_time'] > 0, 'estimated_time应该大于0'

    # 测试主线任务脚本
    main_script = ScriptEngine.create_quest_script('main')
    assert main_script['name'] != '', '脚本name不应该为空'
    assert main_script['reward_value'] > daily_script['reward_value'], '主线任务奖励应该更高'

    # 测试活动任务脚本
    event_script = ScriptEngine.create_quest_script('event')
    assert event_script['name'] != '', '脚本name不应该为空'

    print('  ✓ 任务脚本创建测试通过')
    return True


def test_script_simulation():
    """测试脚本模拟执行"""
    print('测试4: 脚本模拟执行...')

    script = {
        'name': '测试脚本',
        'steps': ['步骤1', '步骤2'],
        'efficiency': 80,
        'risk_level': 'medium',
        'reward_value': 100
    }

    result = ScriptEngine.execute_simulation(script, 10)

    assert 'success_rate' in result, '结果应该有success_rate字段'
    assert 'actual_time' in result, '结果应该有actual_time字段'
    assert 'reward' in result, '结果应该有reward字段'
    assert 'status' in result, '结果应该有status字段'
    assert 0 <= result['success_rate'] <= 100, 'success_rate应该在0-100之间'
    assert result['actual_time'] > 0, 'actual_time应该大于0'
    assert result['status'] in ['completed', 'failed'], 'status应该是有效值'

    print('  ✓ 脚本模拟执行测试通过')
    return True


def test_ai_training():
    """测试AI训练"""
    print('测试5: AI训练...')

    trainer = AITrainer('moba')
    result = trainer.train(episodes=500)

    assert 'episodes' in result, '结果应该有episodes字段'
    assert 'avg_reward' in result, '结果应该有avg_reward字段'
    assert 'final_win_rate' in result, '结果应该有final_win_rate字段'
    assert 'learning_curve' in result, '结果应该有learning_curve字段'
    assert 'q_table_size' in result, '结果应该有q_table_size字段'

    assert result['episodes'] == 500, 'episodes应该匹配'
    assert 0 <= result['final_win_rate'] <= 100, 'final_win_rate应该在0-100之间'
    assert len(result['learning_curve']) > 0, 'learning_curve不应该为空'

    print('  ✓ AI训练测试通过')
    return True


def test_moba_strategy():
    """测试MOBA策略生成"""
    print('测试6: MOBA策略生成...')

    trainer = AITrainer('moba')

    # 优势局策略
    winning_state = {
        'team_gold': [8000, 5000],
        'team_kills': [15, 5],
        'team_towers': [5, 1],
        'team_dragons': [3, 0]
    }
    winning_strategy = trainer.generate_strategy(winning_state)
    assert 'strategy' in winning_strategy, '应该有strategy字段'
    assert 'priority' in winning_strategy, '应该有priority字段'
    assert 'confidence' in winning_strategy, '应该有confidence字段'
    assert winning_strategy['strategy'] in ['aggressive', 'defensive', 'balanced'], 'strategy应该是有效值'

    # 劣势局策略
    losing_state = {
        'team_gold': [4000, 7000],
        'team_kills': [3, 12],
        'team_towers': [1, 4],
        'team_dragons': [0, 2]
    }
    losing_strategy = trainer.generate_strategy(losing_state)
    assert losing_strategy['strategy'] in ['aggressive', 'defensive', 'balanced'], 'strategy应该是有效值'

    print('  ✓ MOBA策略生成测试通过')
    return True


def test_chess_strategy():
    """测试国际象棋策略生成"""
    print('测试7: 国际象棋策略生成...')

    trainer = AITrainer('chess')

    # 均势状态
    equal_state = {
        'board': GameState('chess').state['board'],
        'turn': 'white',
        'pieces': {'white': 16, 'black': 16},
        'moves': 10
    }
    equal_strategy = trainer.generate_strategy(equal_state)
    assert 'strategy' in equal_strategy, '应该有strategy字段'
    assert 'move_type' in equal_strategy, '应该有move_type字段'
    assert equal_strategy['strategy'] in ['aggressive', 'defensive', 'balanced'], 'strategy应该是有效值'

    # 优势状态
    advantage_state = {
        'board': GameState('chess').state['board'],
        'turn': 'white',
        'pieces': {'white': 16, 'black': 14},
        'moves': 10
    }
    advantage_strategy = trainer.generate_strategy(advantage_state)
    assert advantage_strategy['strategy'] in ['aggressive', 'defensive', 'balanced'], 'strategy应该是有效值'

    print('  ✓ 国际象棋策略生成测试通过')
    return True


def test_fps_strategy():
    """测试FPS策略生成"""
    print('测试8: FPS策略生成...')

    trainer = AITrainer('fps')

    # 优势局
    winning_state = {
        'team_score': [15, 10],
        'team_kills': [40, 30],
        'team_deaths': [20, 30],
        'players_alive': [5, 3],
        'bomb_planted': False
    }
    winning_strategy = trainer.generate_strategy(winning_state)
    assert 'strategy' in winning_strategy, '应该有strategy字段'
    assert 'position' in winning_strategy, '应该有position字段'
    assert winning_strategy['strategy'] in ['aggressive', 'defensive', 'balanced'], 'strategy应该是有效值'

    # 劣势局
    losing_state = {
        'team_score': [10, 15],
        'team_kills': [30, 40],
        'team_deaths': [30, 20],
        'players_alive': [3, 5],
        'bomb_planted': False
    }
    losing_strategy = trainer.generate_strategy(losing_state)
    assert losing_strategy['strategy'] in ['aggressive', 'defensive', 'balanced'], 'strategy应该是有效值'

    print('  ✓ FPS策略生成测试通过')
    return True


def test_game_balance_analysis():
    """测试游戏平衡性分析"""
    print('测试9: 游戏平衡性分析...')

    # 生成模拟游戏数据
    game_data = []
    for i in range(100):
        game_data.append({
            'winner': random.choice(['A', 'B', 'C']),
            'roles': random.sample(['warrior', 'mage', 'archer', 'support'], k=random.randint(2, 4))
        })

    analysis = GameAnalyzer.analyze_balance(game_data)

    assert 'balance_score' in analysis, '分析结果应该有balance_score字段'
    assert 'overpowered' in analysis, '分析结果应该有overpowered字段'
    assert 'underpowered' in analysis, '分析结果应该有underpowered字段'
    assert 'recommendations' in analysis, '分析结果应该有recommendations字段'

    assert 0 <= analysis['balance_score'] <= 100, 'balance_score应该在0-100之间'
    assert isinstance(analysis['overpowered'], list), 'overpowered应该是列表'
    assert isinstance(analysis['underpowered'], list), 'underpowered应该是列表'

    print('  ✓ 游戏平衡性分析测试通过')
    return True


def test_player_behavior_analysis():
    """测试玩家行为分析"""
    print('测试10: 玩家行为分析...')

    # 生成模拟玩家数据
    player_data = []
    for i in range(100):
        play_time = random.choice([30, 60, 120, 180, 240])
        player_data.append({
            'play_time': play_time,
            'sessions': random.randint(1, 30),
            'spending': random.randint(0, 1000)
        })

    analysis = GameAnalyzer.analyze_player_behavior(player_data)

    assert 'total_players' in analysis, '分析结果应该有total_players字段'
    assert 'avg_play_time' in analysis, '分析结果应该有avg_play_time字段'
    assert 'avg_sessions' in analysis, '分析结果应该有avg_sessions字段'
    assert 'player_distribution' in analysis, '分析结果应该有player_distribution字段'
    assert 'insights' in analysis, '分析结果应该有insights字段'

    assert analysis['total_players'] == 100, 'total_players应该正确'
    assert analysis['avg_play_time'] > 0, 'avg_play_time应该大于0'
    assert 'casual' in analysis['player_distribution'], '应该有casual玩家分类'
    assert 'core' in analysis['player_distribution'], '应该有core玩家分类'
    assert 'hardcore' in analysis['player_distribution'], '应该有hardcore玩家分类'

    # 检查玩家分布总和接近100%
    distribution = analysis['player_distribution']
    total = distribution['casual'] + distribution['core'] + distribution['hardcore']
    assert 95 <= total <= 105, f'玩家分布总和应该在95-105%之间, 实际是{total}%'

    print('  ✓ 玩家行为分析测试通过')
    return True


def test_outcome_prediction():
    """测试结果预测"""
    print('测试11: 结果预测...')

    # MOBA游戏预测
    moba_state = GameState('moba').state
    moba_prediction = GameAnalyzer.predict_outcome(moba_state)
    assert 'predicted_winner' in moba_prediction, '预测结果应该有predicted_winner字段'
    assert 'confidence' in moba_prediction, '预测结果应该有confidence字段'
    assert 'key_factors' in moba_prediction, '预测结果应该有key_factors字段'
    assert 0 <= moba_prediction['confidence'] <= 100, 'confidence应该在0-100之间'

    # FPS游戏预测
    fps_state = GameState('fps').state
    fps_prediction = GameAnalyzer.predict_outcome(fps_state)
    assert 'predicted_winner' in fps_prediction, '预测结果应该有predicted_winner字段'
    assert fps_prediction['confidence'] >= 0, 'confidence应该>=0'

    print('  ✓ 结果预测测试通过')
    return True


def test_strategy_optimization():
    """测试策略优化"""
    print('测试12: 策略优化...')

    base_strategy = {
        'strategy': 'balanced',
        'confidence': 70
    }

    # 优化胜率
    winrate_optimization = StrategyOptimizer.optimize_strategy(base_strategy, 'winrate')
    assert 'original_strategy' in winrate_optimization, '应该有original_strategy字段'
    assert 'optimized_strategy' in winrate_optimization, '应该有optimized_strategy字段'
    assert 'original_confidence' in winrate_optimization, '应该有original_confidence字段'
    assert 'optimized_confidence' in winrate_optimization, '应该有optimized_confidence字段'
    assert 'improvements' in winrate_optimization, '应该有improvements字段'
    assert winrate_optimization['optimized_confidence'] >= base_strategy['confidence'], '优化后置信度应该提升'

    # 优化效率
    efficiency_optimization = StrategyOptimizer.optimize_strategy(base_strategy, 'efficiency')
    assert 'improvements' in efficiency_optimization, '应该有improvements字段'
    assert len(efficiency_optimization['improvements']) > 0, '应该有改进建议'

    print('  ✓ 策略优化测试通过')
    return True


def test_full_script_workflow():
    """测试完整的脚本创建和执行流程"""
    print('测试13: 完整脚本创建和执行流程...')

    # 创建脚本
    script = create_script('moba', 'farming')
    assert 'name' in script, '脚本应该有name'
    assert 'steps' in script, '脚本应该有steps'

    # 执行脚本
    result = ScriptEngine.execute_simulation(script, 10)
    assert 'status' in result, '执行结果应该有status'

    print('  ✓ 完整脚本创建和执行流程测试通过')
    return True


def test_full_ai_workflow():
    """测试完整的AI训练和策略生成流程"""
    print('测试14: 完整AI训练和策略生成流程...')

    # 训练AI
    training_result = train_ai('moba', 200)
    assert 'final_win_rate' in training_result, '训练结果应该有final_win_rate'

    # 生成策略
    game_state = GameState('moba').state
    strategy = generate_strategy('moba', game_state)
    assert 'strategy' in strategy, '策略应该有strategy字段'

    print('  ✓ 完整AI训练和策略生成流程测试通过')
    return True


def test_full_analysis_workflow():
    """测试完整的游戏分析流程"""
    print('测试15: 完整游戏分析流程...')

    # 分析平衡性
    game_data = [
        {'winner': 'A', 'roles': ['warrior', 'mage']},
        {'winner': 'B', 'roles': ['archer', 'support']},
        {'winner': 'A', 'roles': ['warrior', 'support']}
    ]
    balance_result = analyze_game_balance(game_data)
    assert 'balance_score' in balance_result, '平衡性分析应该有balance_score'

    # 分析玩家行为
    player_data = [
        {'play_time': 60, 'sessions': 10, 'spending': 100},
        {'play_time': 120, 'sessions': 20, 'spending': 500}
    ]
    behavior_result = GameAnalyzer.analyze_player_behavior(player_data)
    assert 'total_players' in behavior_result, '玩家行为分析应该有total_players'

    print('  ✓ 完整游戏分析流程测试通过')
    return True


def test_full_prediction_workflow():
    """测试完整的预测和优化流程"""
    print('测试16: 完整预测和优化流程...')

    # 预测结果
    moba_state = GameState('moba').state
    prediction = predict_game_outcome(moba_state)
    assert 'predicted_winner' in prediction, '预测应该有predicted_winner'

    # 优化策略
    base_strategy = {
        'strategy': 'balanced',
        'confidence': 70
    }
    optimized = StrategyOptimizer.optimize_strategy(base_strategy, 'winrate')
    assert 'optimized_confidence' in optimized, '优化应该有optimized_confidence'

    print('  ✓ 完整预测和优化流程测试通过')
    return True


def run_all_tests():
    """运行所有测试"""
    print('=' * 60)
    print('开始测试游戏AI系统')
    print('=' * 60)

    tests = [
        test_game_state_generation,
        test_farming_script_creation,
        test_quest_script_creation,
        test_script_simulation,
        test_ai_training,
        test_moba_strategy,
        test_chess_strategy,
        test_fps_strategy,
        test_game_balance_analysis,
        test_player_behavior_analysis,
        test_outcome_prediction,
        test_strategy_optimization,
        test_full_script_workflow,
        test_full_ai_workflow,
        test_full_analysis_workflow,
        test_full_prediction_workflow
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f'  ✗ {test.__name__} 失败: {e}')
            failed += 1

    print('=' * 60)
    print(f'测试完成: {passed} 通过, {failed} 失败')
    print('=' * 60)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    import sys
    sys.exit(0 if success else 1)
