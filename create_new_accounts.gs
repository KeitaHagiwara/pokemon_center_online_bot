// ヘッダー行数を設定
const headerRow = 3
const dummyNameSheetName = "ダミー名前"
const maxCharsStreetAddress = 16
const maxCharsBuilding = 16

function createNewUser() {

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const startRow = headerRow + 1; // データ開始行（4行目）

  // ヘッダー辞書を取得
  const headerColumns = createHeaderColumns("accounts", headerRow);

  // 必要な列番号を取得
  const emailCol = headerColumns["メールアドレス"];
  const accountCreatedCol = headerColumns["アカウント作成"];
  const passwordCol = headerColumns["パスワード"];
  const lastNameCol = headerColumns["姓"];
  const firstNameCol = headerColumns["名"];
  const lastNameKanaCol = headerColumns["セイ"];
  const firstNameKanaCol = headerColumns["メイ"];
  const lastNameRomeCol = headerColumns["Sei"];
  const firstNameRomeCol = headerColumns["Mei"];
  const phoneNumberCol = headerColumns["電話番号"];
  const birthdayCol = headerColumns["誕生日"];
  const postalCodeCol = headerColumns["郵便番号"];
  const streetAddressCol = headerColumns["番地"];
  const buildingCol = headerColumns["建物名・部屋番号"];

  // マスタとして設定するデータを取得
  const passwordValue = sheet.getRange("E2").getValue();  // パスワードマスタ
  const lastNameValue = sheet.getRange("F2").getValue();  // 姓マスタ
  const lastNameKanaValue = sheet.getRange("H2").getValue();  // セイマスタ
  const lastNameRomeValue = sheet.getRange("J2").getValue();  // Seiマスタ
  const birthdayValue = sheet.getRange("L2").getValue();  // 誕生日マスタ
  const postalCodeValue = sheet.getRange("M2").getValue();  // 郵便番号マスタ
  const streetAddressValue = sheet.getRange("N2").getValue(); // 番地マスタ
  const buildingValue = sheet.getRange("O2").getValue();  // 建物名・部屋番号マスタ

  // メールアドレス列の最終行を取得
  const lastRow = sheet.getRange(startRow, emailCol, sheet.getLastRow() - startRow + 1, 1)
    .getValues()
    .reduce((last, row, index) => {
      return row[0] !== "" ? startRow + index : last;
    }, startRow);

  Logger.log("処理対象行: " + startRow + "行目から" + lastRow + "行目まで");

  // データ行をループ処理
  for (let row = startRow; row <= lastRow; row++) {
    const index = row - headerRow;

    // メールアドレスが空白の場合はスキップ
    const email = sheet.getRange(row, emailCol).getValue();
    if (email === "") {
      continue;
    }

    // 「アカウント作成」列の値を取得
    const accountCreated = sheet.getRange(row, accountCreatedCol).getValue();

    // 「ダミー名前」シートのヘッダーカラムを取得
    const headerColumnsDummy = createHeaderColumns(dummyNameSheetName, 1);

    // 「済み」になっていない場合のみ処理
    if (accountCreated !== "済み") {
      // ダミーの情報を生成
      dummyRow = getRandomRowFromDummyNames();
      // dummyLastName = dummyRow[headerColumnsDummy["姓"] - 1]
      // dummyLastNameKana = dummyRow[headerColumnsDummy["セイ"] - 1]
      // dummyLastNameRome = convertToUpperCase(dummyRow[headerColumnsDummy["Sei"] - 1])
      dummyFirstName = dummyRow[headerColumnsDummy["名"] - 1]
      dummyFirstNameKana = dummyRow[headerColumnsDummy["メイ"] - 1]
      dummyFirstNameRome = convertToUpperCase(dummyRow[headerColumnsDummy["Mei"] - 1])
      dummyphoneNumber = generateDummyPhoneNumber()

      // 番地のランダム値を生成する
      let streetAddressPrefix = ""
      const streetAddressValueWithSuffix = streetAddressValue + "-" + index
      // 先頭ランダム文字列なしで15文字を超える場合はエラーとする
      if (streetAddressValueWithSuffix.length > maxCharsStreetAddress - 1) {
        Browser.msgBox(`番地が${maxCharsStreetAddress}文字を超えるため、ランダム文字列を付与できません。(${row}行目)`)
        // 処理を停止する
        return
      } else {
        streetAddressPrefix =  generateRandomChars(
          maxCharsStreetAddress - streetAddressValueWithSuffix.length,
          streetAddressValueWithSuffix
        )
      }

      // 建物名・部屋番号のランダム値を生成する
      let buildingPrefix = ""
      const buildingValueWithSuffix = buildingValue + "-" + index
      if (buildingValueWithSuffix > maxCharsStreetAddress - 1){
        Browser.msgBox(`建物名・部屋番号が${maxCharsBuilding}文字を超えるため、ランダム文字列を付与できません。(${row}行目)`)
        // 処理を停止する
        return
      } else {
        buildingPrefix = generateRandomChars(
          maxCharsBuilding - buildingValueWithSuffix.length,
          buildingValueWithSuffix
        )
      }

      const streetAddressValueUnique = streetAddressPrefix + streetAddressValueWithSuffix
      const buildingValueUnique = buildingPrefix + buildingValueWithSuffix

      // 各列に値を設定
      sheet.getRange(row, passwordCol).setValue(passwordValue);
      sheet.getRange(row, lastNameCol).setValue(lastNameValue);
      sheet.getRange(row, firstNameCol).setValue(dummyFirstName);
      sheet.getRange(row, lastNameKanaCol).setValue(lastNameKanaValue);
      sheet.getRange(row, firstNameKanaCol).setValue(dummyFirstNameKana);
      sheet.getRange(row, lastNameRomeCol).setValue(lastNameRomeValue);
      sheet.getRange(row, firstNameRomeCol).setValue(dummyFirstNameRome);
      sheet.getRange(row, phoneNumberCol).setValue(dummyphoneNumber);
      sheet.getRange(row, birthdayCol).setValue(birthdayValue);
      sheet.getRange(row, postalCodeCol).setValue(postalCodeValue);
      sheet.getRange(row, streetAddressCol).setValue(streetAddressValueUnique)
      sheet.getRange(row, buildingCol).setValue(buildingValueUnique);

      Logger.log(row + "行目を処理しました");
    }
  }

  Logger.log("処理完了");

}


/**
 * 3行目のヘッダーから列名と列番号の辞書を作成する
 * @return {Object} ヘッダー名をキー、列番号を値とする辞書
 */
function createHeaderColumns(sheetName, headerRow=3) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(sheetName);

  // 3行目のデータを取得
  const lastColumn = sheet.getLastColumn();
  const headers = sheet.getRange(headerRow, 1, 1, lastColumn).getValues()[0];

  // 辞書を作成
  const headerColumns = {};
  headers.forEach((header, index) => {
    if (header !== "") { // 空白セルは除外
      headerColumns[header] = index + 1; // 列番号は1始まり
    }
  });

  return headerColumns;
}

/**
 * カスタム長のShortUUIDを生成する
 * @param {number} length - 生成する文字列の長さ
 * @return {string} 指定長のランダム文字列
 */
// function generateCustomShortUUID(length = 8) {
//   const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
//   let result = '';

//   for (let i = 0; i < length; i++) {
//     const randomIndex = Math.floor(Math.random() * chars.length);
//     result += chars[randomIndex];
//   }

//   return result;
// }

/**
 * ダミーの携帯電話番号を生成する（ハイフンなし）
 * 080, 090, 070のいずれかから始まる11桁
 * @return {string} ダミー携帯電話番号（例: 09012345678）
 */
function generateDummyPhoneNumber() {
  const prefixes = ["080", "090", "070"];
  const randomPrefix = prefixes[Math.floor(Math.random() * prefixes.length)];

  // 残り8桁をランダム生成
  let remainingDigits = "";
  for (let i = 0; i < 8; i++) {
    remainingDigits += Math.floor(Math.random() * 10);
  }

  return randomPrefix + remainingDigits;
}

/**
 * 「ダミー名前」シートからランダムで1行を取得する
 * @return {Array} ランダムに選ばれた行のデータ配列
 */
function getRandomRowFromDummyNames() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(dummyNameSheetName);
  headerColDict = createHeaderColumns(dummyNameSheetName, 1)
  Logger.log(headerColDict);

  if (!sheet) {
    throw new Error(`${dummyNameSheetName}という名前のシートが見つかりません`);
  }

  // データ範囲を取得（ヘッダー行を除く）
  const lastRow = sheet.getLastRow();
  const lastColumn = sheet.getLastColumn();

  if (lastRow < 2) {
    throw new Error("データが存在しません（ヘッダー行のみ）");
  }

  // 2行目から最終行までの範囲でランダムな行番号を生成
  const randomRow = Math.floor(Math.random() * (lastRow - 1)) + 2;

  // ランダムな行のデータを取得
  const rowData = sheet.getRange(randomRow, 1, 1, lastColumn).getValues()[0];

  return rowData;
}


/**
 * 半角英数字を全角に変換する
 * @param {string} text - 変換対象のテキスト
 * @return {string} 全角に変換されたテキスト
 */
function convertHalfToFull(text) {
  if (!text) return text;

  return text.replace(/[A-Za-z0-9]/g, function(char) {
    // 半角文字コードから全角文字コードへの変換
    // 半角A-Z: 0x41-0x5A → 全角A-Z: 0xFF21-0xFF3A (差分 0xFEE0)
    // 半角a-z: 0x61-0x7A → 全角a-z: 0xFF41-0xFF5A (差分 0xFEE0)
    // 半角0-9: 0x30-0x39 → 全角0-9: 0xFF10-0xFF19 (差分 0xFEE0)
    return String.fromCharCode(char.charCodeAt(0) + 0xFEE0);
  });
}

/**
 * 小文字のローマ字を大文字に変換する
 * @param {string} text - 変換対象のテキスト
 * @return {string} 大文字に変換されたテキスト
 */
function convertToUpperCase(text) {
  if (!text) return text;
  return text.toUpperCase();
}

/**
 * 記号・数字・アルファベットを含むランダムな文字列を生成する関数
 * 最大3文字まで
 *
 * @param {number} length - 生成する文字数（1〜3）
 * @param {string} seedValue - シード値（元の文字列）
 * @return {string} ランダムな文字列
 */
function generateRandomChars(length, seedValue) {
  if (length <= 0) return '';
  if (length > 3) length = 3; // 最大3文字に制限

  // 各カテゴリの文字
  const symbols = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~';
  const digits = '0123456789';
  const letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';

  // シード付き乱数生成器を初期化
  const hash = hashCode(String(seedValue));
  const rng = new SeededRandom(hash);

  // 各カテゴリから1文字ずつ選択
  const symbol = symbols[Math.floor(rng.random() * symbols.length)];
  const digit = digits[Math.floor(rng.random() * digits.length)];
  const letter = letters[Math.floor(rng.random() * letters.length)];

  if (length === 1) {
    // 1文字の場合：記号、数字、アルファベットのいずれか
    const chars = [symbol, digit, letter];
    return chars[Math.floor(rng.random() * 3)];
  } else if (length === 2) {
    // 2文字の場合：記号、数字、アルファベットから2つ選択
    const chars = [symbol, digit, letter];
    // ランダムに2つ選択
    const first = Math.floor(rng.random() * 3);
    let second = Math.floor(rng.random() * 3);
    // 同じものを選ばないようにする
    while (second === first) {
      second = Math.floor(rng.random() * 3);
    }
    return chars[first] + chars[second];
  } else {
    // 3文字の場合：記号・数字・アルファベットを全て含む
    const threeChars = [symbol, digit, letter];
    // ランダムな順序で配置
    for (let i = threeChars.length - 1; i > 0; i--) {
      const j = Math.floor(rng.random() * (i + 1));
      [threeChars[i], threeChars[j]] = [threeChars[j], threeChars[i]];
    }
    return threeChars.join('');
  }
}

/**
 * 文字列のハッシュコードを計算
 *
 * @param {string} str - ハッシュ化する文字列
 * @return {number} ハッシュ値
 */
function hashCode(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // 32bit整数に変換
  }
  return Math.abs(hash);
}

/**
 * シード付き乱数生成器
 */
class SeededRandom {
  constructor(seed) {
    // 現在の日時をミリ秒単位で取得してseedと組み合わせる
    const timestamp = new Date().getTime();
    const combinedSeed = seed ^ timestamp; // XOR演算で組み合わせ

    this.seed = combinedSeed % 2147483647;
    if (this.seed <= 0) this.seed += 2147483646;
  }

  random() {
    this.seed = (this.seed * 16807) % 2147483647;
    return (this.seed - 1) / 2147483646;
  }
}
