import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import 'package:aiomobile/core/error/failures.dart';
import 'package:aiomobile/features/auth/domain/entities/user.dart';
import 'package:aiomobile/features/auth/domain/repositories/auth_repository.dart';
import 'package:aiomobile/features/auth/domain/usecases/login_usecase.dart';

class MockAuthRepository extends Mock implements AuthRepository {}

void main() {
  late MockAuthRepository repo;
  late LoginUseCase useCase;

  const tUser = User(id: '1', email: 'test@aio.dev');
  const tParams = LoginParams(email: 'test@aio.dev', password: 'pass123');

  setUp(() {
    repo = MockAuthRepository();
    useCase = LoginUseCase(repo);
  });

  test('returns data from repository on success', () async {
    when(() => repo.login(email: tParams.email, password: tParams.password))
        .thenAnswer((_) async => (
              data: (user: tUser, accessToken: 'tok'),
              failure: null,
            ));

    final result = await useCase(tParams);

    expect(result.failure, isNull);
    expect(result.data?.user, tUser);
    expect(result.data?.accessToken, 'tok');
  });

  test('returns failure from repository on error', () async {
    when(() => repo.login(email: tParams.email, password: tParams.password))
        .thenAnswer((_) async => (
              data: null,
              failure: const ServerFailure('Unauthorized', statusCode: 401),
            ));

    final result = await useCase(tParams);

    expect(result.data, isNull);
    expect(result.failure, isA<ServerFailure>());
    expect((result.failure as ServerFailure).statusCode, 401);
  });
}
