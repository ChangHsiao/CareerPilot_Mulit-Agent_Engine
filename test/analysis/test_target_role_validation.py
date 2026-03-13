import pytest
from pydantic import ValidationError
from src.features.analysis.schemas import TargetPosition

def test_target_role_validation_success():
    """測試完全吻合的 Literal 字串能否正常通過"""
    tp = TargetPosition(
        role="資料科學家/數據分析師",
        match_score="85%",
        gap_description="測試描述"
    )
    assert tp.role == "資料科學家/數據分析師"

def test_target_role_validation_auto_correction():
    """測試常見縮寫（如資料科學家）能否被自動修復為完整字串"""
    # 測試 LLM 最常犯的縮寫錯誤
    tp1 = TargetPosition(
        role="資料科學家",
        match_score="80%",
        gap_description="測試描述"
    )
    assert tp1.role == "資料科學家/數據分析師"

    # 測試另一個常見縮寫
    tp2 = TargetPosition(
        role="前端",
        match_score="90%",
        gap_description="測試描述"
    )
    assert tp2.role == "前端工程師"

def test_target_role_validation_failure():
    """測試真的亂填的字串是否依然會被 Pydantic 擋下拋出 ValidationError"""
    with pytest.raises(ValidationError) as excinfo:
        TargetPosition(
            role="魔法師",
            match_score="100%",
            gap_description="測試描述"
        )
    
    # 確認錯誤訊息包含我們預期的字眼
    assert "Input should be '前端工程師', '後端工程師'" in str(excinfo.value) or "魔法師" in str(excinfo.value)

if __name__ == "__main__":
    print("====== 開始測試 TargetPosition Role 自動修復機制 ======")
    try:
        test_target_role_validation_success()
        print("✅ 測試成功：完整字串正常通過")
        
        test_target_role_validation_auto_correction()
        print("✅ 測試成功：『資料科學家』等縮寫已成功被自動修復為完整字串")
        
        test_target_role_validation_failure()
        print("✅ 測試成功：未知的亂數職位正確地被 Pydantic 攔截")
        
        print("\n🎉 所有測試皆通過！自動修復機制運作正常。")
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
