import Decimal from "decimal.js";

export type Money = string;

export const compareMoneyToZero = (amount: Money): number =>
  new Decimal(amount).comparedTo(0);
