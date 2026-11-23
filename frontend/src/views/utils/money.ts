import Decimal from "decimal.js";

import { Money } from "../types/money";

export const compareMoneyToZero = (amount: Money): number =>
  new Decimal(amount).comparedTo(0);

export const convertTenThousandYenToYen = (amount: string): number =>
  Math.round(Number(amount) * 10_000);
